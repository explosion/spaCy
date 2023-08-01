import random
import shutil
import sys
from pathlib import Path
from timeit import default_timer as timer
from typing import (
    IO,
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Union,
)

from thinc.api import Config, Optimizer, constant, fix_random_seed, set_gpu_allocator
from wasabi import Printer

from ..errors import Errors
from ..schemas import ConfigSchemaTraining
from ..util import logger, registry, resolve_dot_names
from .example import Example

if TYPE_CHECKING:
    from ..language import Language  # noqa: F401


DIR_MODEL_BEST = "model-best"
DIR_MODEL_LAST = "model-last"


def train(
    nlp: "Language",
    output_path: Optional[Path] = None,
    *,
    use_gpu: int = -1,
    stdout: IO = sys.stdout,
    stderr: IO = sys.stderr,
) -> Tuple["Language", Optional[Path]]:
    """Train a pipeline.

    nlp (Language): The initialized nlp object with the full config.
    output_path (Optional[Path]): Optional output path to save trained model to.
    use_gpu (int): Whether to train on GPU. Make sure to call require_gpu
        before calling this function.
    stdout (file): A file-like object to write output messages. To disable
        printing, set to io.StringIO.
    stderr (file): A second file-like object to write output messages. To disable
        printing, set to io.StringIO.

    RETURNS (tuple): The final nlp object and the path to the exported model.
    """
    # We use no_print here so we can respect the stdout/stderr options.
    msg = Printer(no_print=True)
    # Create iterator, which yields out info after each optimization step.
    config = nlp.config.interpolate()
    if config["training"]["seed"] is not None:
        fix_random_seed(config["training"]["seed"])
    allocator = config["training"]["gpu_allocator"]
    if use_gpu >= 0 and allocator:
        set_gpu_allocator(allocator)
    T = registry.resolve(config["training"], schema=ConfigSchemaTraining)
    dot_names = [T["train_corpus"], T["dev_corpus"]]
    train_corpus, dev_corpus = resolve_dot_names(config, dot_names)
    optimizer = T["optimizer"]
    score_weights = T["score_weights"]
    batcher = T["batcher"]
    train_logger = T["logger"]
    before_to_disk = create_before_to_disk_callback(T["before_to_disk"])
    before_update = T["before_update"]

    # Helper function to save checkpoints. This is a closure for convenience,
    # to avoid passing in all the args all the time.
    def save_checkpoint(is_best):
        with nlp.use_params(optimizer.averages):
            before_to_disk(nlp).to_disk(output_path / DIR_MODEL_LAST)
        if is_best:
            # Avoid saving twice (saving will be more expensive than
            # the dir copy)
            if (output_path / DIR_MODEL_BEST).exists():
                shutil.rmtree(output_path / DIR_MODEL_BEST)
            shutil.copytree(output_path / DIR_MODEL_LAST, output_path / DIR_MODEL_BEST)

    # Components that shouldn't be updated during training
    frozen_components = T["frozen_components"]
    # Components that should set annotations on update
    annotating_components = T["annotating_components"]
    # Create iterator, which yields out info after each optimization step.
    training_step_iterator = train_while_improving(
        nlp,
        optimizer,
        create_train_batches(nlp, train_corpus, batcher, T["max_epochs"]),
        create_evaluation_callback(nlp, dev_corpus, score_weights),
        dropout=T["dropout"],
        accumulate_gradient=T["accumulate_gradient"],
        patience=T["patience"],
        max_steps=T["max_steps"],
        eval_frequency=T["eval_frequency"],
        exclude=frozen_components,
        annotating_components=annotating_components,
        before_update=before_update,
    )
    clean_output_dir(output_path)
    stdout.write(msg.info(f"Pipeline: {nlp.pipe_names}") + "\n")
    if frozen_components:
        stdout.write(msg.info(f"Frozen components: {frozen_components}") + "\n")
    if annotating_components:
        stdout.write(
            msg.info(f"Set annotations on update for: {annotating_components}") + "\n"
        )
    stdout.write(msg.info(f"Initial learn rate: {optimizer.learn_rate}") + "\n")
    with nlp.select_pipes(disable=frozen_components):
        log_step, finalize_logger = train_logger(nlp, stdout, stderr)
    try:
        for batch, info, is_best_checkpoint in training_step_iterator:
            if is_best_checkpoint is not None:
                with nlp.select_pipes(disable=frozen_components):
                    update_meta(T, nlp, info)
                if output_path is not None:
                    save_checkpoint(is_best_checkpoint)
                    info["output_path"] = str(output_path / DIR_MODEL_LAST)
            log_step(info if is_best_checkpoint is not None else None)
    except Exception as e:
        if output_path is not None:
            stdout.write(
                msg.warn(
                    f"Aborting and saving the final best model. "
                    f"Encountered exception: {repr(e)}"
                )
                + "\n"
            )
        raise e
    finally:
        finalize_logger()
        if output_path is not None:
            save_checkpoint(False)
    # This will only run if we did't hit an error
    if optimizer.averages:
        nlp.use_params(optimizer.averages)
    if output_path is not None:
        stdout.write(
            msg.good("Saved pipeline to output directory", output_path / DIR_MODEL_LAST)
            + "\n"
        )
        return (nlp, output_path / DIR_MODEL_LAST)
    else:
        return (nlp, None)


def train_while_improving(
    nlp: "Language",
    optimizer: Optimizer,
    train_data,
    evaluate,
    *,
    dropout: float,
    eval_frequency: int,
    accumulate_gradient: int,
    patience: int,
    max_steps: int,
    exclude: List[str],
    annotating_components: List[str],
    before_update: Optional[Callable[["Language", Dict[str, Any]], None]],
):
    """Train until an evaluation stops improving. Works as a generator,
    with each iteration yielding a tuple `(batch, info, is_best_checkpoint)`,
    where info is a dict, and is_best_checkpoint is in [True, False, None] --
    None indicating that the iteration was not evaluated as a checkpoint.
    The evaluation is conducted by calling the evaluate callback.

    Positional arguments:
        nlp: The spaCy pipeline to evaluate.
        optimizer: The optimizer callable.
        train_data (Iterable[Batch]): A generator of batches, with the training
            data. Each batch should be a Sized[Tuple[Input, Annot]]. The training
            data iterable needs to take care of iterating over the epochs and
            shuffling.
        evaluate (Callable[[], Tuple[float, Any]]): A callback to perform evaluation.
            The callback should take no arguments and return a tuple
            `(main_score, other_scores)`. The main_score should be a float where
            higher is better. other_scores can be any object.

    Every iteration, the function yields out a tuple with:

    * batch: A list of Example objects.
    * info: A dict with various information about the last update (see below).
    * is_best_checkpoint: A value in None, False, True, indicating whether this
        was the best evaluation so far. You should use this to save the model
        checkpoints during training. If None, evaluation was not conducted on
        that iteration. False means evaluation was conducted, but a previous
        evaluation was better.

    The info dict provides the following information:

        epoch (int): How many passes over the data have been completed.
        step (int): How many steps have been completed.
        score (float): The main score from the last evaluation.
        other_scores: : The other scores from the last evaluation.
        losses: The accumulated losses throughout training.
        checkpoints: A list of previous results, where each result is a
            (score, step, epoch) tuple.
    """
    if isinstance(dropout, float):
        dropouts = constant(dropout)
    else:
        dropouts = dropout
    results = []
    losses: Dict[str, float] = {}
    words_seen = 0
    start_time = timer()
    for step, (epoch, batch) in enumerate(train_data):
        if before_update:
            before_update_args = {"step": step, "epoch": epoch}
            before_update(nlp, before_update_args)
        dropout = next(dropouts)  # type: ignore
        for subbatch in subdivide_batch(batch, accumulate_gradient):
            nlp.update(
                subbatch,
                drop=dropout,
                losses=losses,
                sgd=False,  # type: ignore[arg-type]
                exclude=exclude,
                annotates=annotating_components,
            )
        # TODO: refactor this so we don't have to run it separately in here
        for name, proc in nlp.pipeline:
            if (
                name not in exclude
                and hasattr(proc, "is_trainable")
                and proc.is_trainable
                and proc.model not in (True, False, None)  # type: ignore[attr-defined]
            ):
                proc.finish_update(optimizer)  # type: ignore[attr-defined]
        optimizer.step_schedules()
        if not (step % eval_frequency):
            if optimizer.averages:
                with nlp.use_params(optimizer.averages):
                    score, other_scores = evaluate()
            else:
                score, other_scores = evaluate()
            results.append((score, step))
            is_best_checkpoint = score == max(results)[0]
        else:
            score, other_scores = (None, None)
            is_best_checkpoint = None
        words_seen += sum(len(eg) for eg in batch)
        info = {
            "epoch": epoch,
            "step": step,
            "score": score,
            "other_scores": other_scores,
            "losses": losses,
            "checkpoints": results,
            "seconds": int(timer() - start_time),
            "words": words_seen,
        }
        yield batch, info, is_best_checkpoint
        if is_best_checkpoint is not None:
            losses = {}
        # Stop if no improvement in `patience` updates (if specified)
        # Negate step value so that the earliest best step is chosen for the
        # same score, i.e. (1.0, 100) is chosen over (1.0, 200)
        best_result = max((r_score, -r_step) for r_score, r_step in results)
        best_step = -best_result[1]
        if patience and (step - best_step) >= patience:
            break
        # Stop if we've exhausted our max steps (if specified)
        if max_steps and step >= max_steps:
            break


def subdivide_batch(batch, accumulate_gradient):
    batch = list(batch)
    batch.sort(key=lambda eg: len(eg.predicted))
    sub_len = len(batch) // accumulate_gradient
    start = 0
    for i in range(accumulate_gradient):
        subbatch = batch[start : start + sub_len]
        if subbatch:
            yield subbatch
        start += len(subbatch)
    subbatch = batch[start:]
    if subbatch:
        yield subbatch


def create_evaluation_callback(
    nlp: "Language", dev_corpus: Callable, weights: Dict[str, float]
) -> Callable[[], Tuple[float, Dict[str, float]]]:
    weights = {key: value for key, value in weights.items() if value is not None}

    def evaluate() -> Tuple[float, Dict[str, float]]:
        nonlocal weights
        try:
            scores = nlp.evaluate(dev_corpus(nlp))
        except KeyError as e:
            raise KeyError(Errors.E900.format(pipeline=nlp.pipe_names)) from e
        # Calculate a weighted sum based on score_weights for the main score.
        # We can only consider scores that are ints/floats, not dicts like
        # entity scores per type etc.
        scores = {key: value for key, value in scores.items() if value is not None}
        weights = {key: value for key, value in weights.items() if key in scores}
        for key, value in scores.items():
            if key in weights and not isinstance(value, (int, float)):
                raise ValueError(Errors.E915.format(name=key, score_type=type(value)))
        try:
            weighted_score = sum(
                scores.get(s, 0.0) * weights.get(s, 0.0) for s in weights
            )
        except KeyError as e:
            keys = list(scores.keys())
            err = Errors.E983.format(dict="score_weights", key=str(e), keys=keys)
            raise KeyError(err) from None
        return weighted_score, scores

    return evaluate


def create_train_batches(
    nlp: "Language",
    corpus: Callable[["Language"], Iterable[Example]],
    batcher: Callable[[Iterable[Example]], Iterable[Example]],
    max_epochs: int,
):
    epoch = 0
    if max_epochs >= 0:
        examples = list(corpus(nlp))  # type: Iterable[Example]
        if not examples:
            # Raise error if no data
            raise ValueError(Errors.E986)
    while max_epochs < 1 or epoch != max_epochs:
        if max_epochs >= 0:
            random.shuffle(examples)  # type: ignore
        else:
            examples = corpus(nlp)
        for batch in batcher(examples):
            yield epoch, batch
        epoch += 1


def update_meta(
    training: Union[Dict[str, Any], Config], nlp: "Language", info: Dict[str, Any]
) -> None:
    nlp.meta["performance"] = {}
    for metric in training["score_weights"]:
        if metric is not None:
            nlp.meta["performance"][metric] = info["other_scores"].get(metric, 0.0)
    for pipe_name in nlp.pipe_names:
        if pipe_name in info["losses"]:
            nlp.meta["performance"][f"{pipe_name}_loss"] = info["losses"][pipe_name]


def create_before_to_disk_callback(
    callback: Optional[Callable[["Language"], "Language"]]
) -> Callable[["Language"], "Language"]:
    from ..language import Language  # noqa: F811

    def before_to_disk(nlp: Language) -> Language:
        if not callback:
            return nlp
        modified_nlp = callback(nlp)
        if not isinstance(modified_nlp, Language):
            err = Errors.E914.format(name="before_to_disk", value=type(modified_nlp))
            raise ValueError(err)
        return modified_nlp

    return before_to_disk


def clean_output_dir(path: Optional[Path]) -> None:
    """Remove an existing output directory. Typically used to ensure that that
    a directory like model-best and its contents aren't just being overwritten
    by nlp.to_disk, which could preserve existing subdirectories (e.g.
    components that don't exist anymore).
    """
    if path is not None and path.exists():
        for subdir in [path / DIR_MODEL_BEST, path / DIR_MODEL_LAST]:
            if subdir.exists():
                try:
                    shutil.rmtree(str(subdir))
                    logger.debug("Removed existing output directory: %s", subdir)
                except Exception as e:
                    raise IOError(Errors.E901.format(path=path)) from e
