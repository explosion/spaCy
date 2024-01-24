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
    Sized,
    Tuple,
    TypeVar,
    Union,
)

from thinc.api import Config, Optimizer, constant
from wasabi import Printer

from .. import ty
from ..errors import Errors
from ..schemas import ConfigSchemaDistill, ConfigSchemaTraining
from ..util import (
    logger,
    registry,
    resolve_dot_names,
    set_gpu_allocator_from_config,
    set_seed_from_config,
)
from .example import Example

if TYPE_CHECKING:
    from ..language import Language  # noqa: F401


DIR_MODEL_BEST = "model-best"
DIR_MODEL_LAST = "model-last"


def distill(
    teacher: "Language",
    student: "Language",
    output_path: Optional[Path] = None,
    *,
    use_gpu: int = -1,
    stdout: IO = sys.stdout,
    stderr: IO = sys.stderr,
) -> Tuple["Language", Optional[Path]]:
    """Distill a student pipeline from a teacher pipeline.

    teacher (Language): The teacher pipeline to distill from.
    student (Language): The student pipeline to distill into.
    output_path (Optional[Path]): Optional output path to save the student
        model to.
    use_gpu (int): Whether to train on GPU. Make sure to call require_gpu
        before calling this function.
    stdout (file): A file-like object to write output messages. To disable
        printing, set to io.StringIO.
    stderr (file): A second file-like object to write output messages. To disable
        printing, set to io.StringIO.

    RETURNS (tuple): The final student nlp object and the path to the exported
        student model.
    """
    # We use no_print here so we can respect the stdout/stderr options.
    msg = Printer(no_print=True)
    # Create iterator, which yields out info after each optimization step.
    config = student.config.interpolate()
    set_seed_from_config(config)
    set_gpu_allocator_from_config(config, use_gpu)
    T = registry.resolve(config["training"], schema=ConfigSchemaTraining)
    D = registry.resolve(config["distillation"], schema=ConfigSchemaDistill)
    dot_names = [D["corpus"], T["dev_corpus"]]
    distill_corpus, dev_corpus = resolve_dot_names(config, dot_names)
    optimizer = D["optimizer"]
    score_weights = T["score_weights"]
    batcher = D["batcher"]
    train_logger = T["logger"]
    before_to_disk = create_before_to_disk_callback(T["before_to_disk"])
    before_update = T["before_update"]
    student_to_teacher = D["student_to_teacher"]

    # Helper function to save checkpoints. This is a closure for convenience,
    # to avoid passing in all the args all the time.
    def save_checkpoint(is_best):
        with student.use_params(optimizer.averages):
            before_to_disk(student).to_disk(output_path / DIR_MODEL_LAST)
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
    training_step_iterator = _distill_loop(
        teacher,
        student,
        optimizer,
        create_distill_batches(student, distill_corpus, batcher, D["max_epochs"]),
        create_evaluation_callback(student, dev_corpus, score_weights),
        dropout=D["dropout"],
        accumulate_gradient=T["accumulate_gradient"],
        max_steps=D["max_steps"],
        eval_frequency=T["eval_frequency"],
        exclude=frozen_components,
        annotating_components=annotating_components,
        before_update=before_update,
        student_to_teacher=student_to_teacher,
    )
    clean_output_dir(output_path)
    stdout.write(msg.info(f"Teacher pipeline: {teacher.pipe_names}") + "\n")
    stdout.write(msg.info(f"Student pipeline: {student.pipe_names}") + "\n")
    if frozen_components:
        stdout.write(msg.info(f"Frozen components: {frozen_components}") + "\n")
    if annotating_components:
        stdout.write(
            msg.info(f"Set annotations on update for: {annotating_components}") + "\n"
        )
    stdout.write(msg.info(f"Initial learn rate: {optimizer.learn_rate(step=0)}") + "\n")
    with student.select_pipes(disable=frozen_components):
        log_step, finalize_logger = train_logger(student, stdout, stderr)
    try:
        for batch, info, is_best_checkpoint in training_step_iterator:
            if is_best_checkpoint is not None:
                with student.select_pipes(disable=frozen_components):
                    update_meta(T, student, info)
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
        student.use_params(optimizer.averages)
    if output_path is not None:
        stdout.write(
            msg.good("Saved pipeline to output directory", output_path / DIR_MODEL_LAST)
            + "\n"
        )
        return (student, output_path / DIR_MODEL_LAST)
    else:
        return (student, None)


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
    set_seed_from_config(config)
    set_gpu_allocator_from_config(config, use_gpu)
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
    stdout.write(msg.info(f"Initial learn rate: {optimizer.learn_rate(step=0)}") + "\n")
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


def _distill_loop(
    teacher: "Language",
    student: "Language",
    optimizer: Optimizer,
    distill_data: Iterable[Tuple[int, List[Example]]],
    evaluate: Callable[[], Tuple[float, Dict[str, float]]],
    *,
    dropout: float,
    eval_frequency: int,
    accumulate_gradient: int,
    max_steps: int,
    exclude: List[str],
    annotating_components: List[str],
    before_update: Optional[Callable[["Language", Dict[str, Any]], None]],
    student_to_teacher: Dict[str, str],
):
    """Distill until the data is exhausted or the maximum number of steps
    has been reached. Works as a generator, with each iteration yielding
    a tuple `(batch, info, is_best_checkpoint)`, where info is a dict, and
    is_best_checkpoint is in [True, False, None] -- None indicating that
    the iteration was not evaluated as a checkpoint. The evaluation is
    conducted by calling the evaluate callback.

    Positional arguments:
        teacher (Language): The teacher pipeline to distill from.
        student (Language): The student pipeline to distill into.
        optimizer: The optimizer callable.
        distill_data (Iterable[List[Example]]): A generator of batches,
            with the distillation data. The distillation data iterable
            needs to take care of iterating over the epochs and shuffling.
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
    for step, (epoch, batch) in enumerate(distill_data):
        if before_update:
            before_update_args = {"step": step, "epoch": epoch}
            before_update(student, before_update_args)
        dropout = dropouts(optimizer.step)
        for subbatch in subdivide_batch(batch, accumulate_gradient):
            student.distill(
                teacher,
                subbatch,
                drop=dropout,
                losses=losses,
                sgd=False,
                exclude=exclude,
                annotates=annotating_components,
                student_to_teacher=student_to_teacher,
            )
        # TODO: refactor this so we don't have to run it separately in here
        for student_name, student_proc in student.pipeline:
            if (
                student_name not in exclude
                and isinstance(student_proc, ty.DistillableComponent)
                and student_proc.is_distillable
                and student_proc.model not in (False, None)  # type: ignore[attr-defined]
            ):
                student_proc.finish_update(optimizer)  # type: ignore[attr-defined]
        optimizer.step_schedules()
        if not (step % eval_frequency):
            if optimizer.averages:
                with student.use_params(optimizer.averages):
                    score, other_scores = evaluate()
            else:
                score, other_scores = evaluate()
            optimizer.last_score = score  # type: ignore[assignment]
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
        # Stop if we've exhausted our max steps (if specified)
        if max_steps and step >= max_steps:
            break


def train_while_improving(
    nlp: "Language",
    optimizer: Optimizer,
    train_data: Iterable[Tuple[int, List[Example]]],
    evaluate: Callable[[], Tuple[float, Dict[str, float]]],
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
        train_data (Iterable[List[Example]]): A generator of batches, with the
            training data. The training data iterable needs to take care of
            iterating over the epochs and shuffling.
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
        dropout = dropouts(optimizer.step)  # type: ignore
        for subbatch in subdivide_batch(batch, accumulate_gradient):
            nlp.update(
                subbatch,
                drop=dropout,
                losses=losses,
                sgd=False,
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
            optimizer.last_score = score  # type: ignore[assignment]
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


ItemT = TypeVar("ItemT", bound=Sized)


def subdivide_batch(
    batch: Iterable[ItemT], accumulate_gradient: int
) -> Iterable[List[ItemT]]:
    batch = list(batch)
    if len(batch):
        # Examples are sorted by their predicted length.
        batch.sort(key=lambda item: len(item))
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


def create_distill_batches(
    nlp: "Language",
    corpus: Callable[["Language"], Iterable[Example]],
    batcher: Callable[[Iterable[Example]], Iterable[List[Example]]],
    max_epochs: int,
) -> Iterable[Tuple[int, List[Example]]]:
    """Create distillation batches. In contrast to training, the corpus
    is normally too large to load into memory and shuffle."""
    epoch = 0
    while max_epochs < 1 or epoch != max_epochs:
        examples = corpus(nlp)
        for batch in batcher(examples):
            yield epoch, batch
        epoch += 1


def create_train_batches(
    nlp: "Language",
    corpus: Callable[["Language"], Iterable[Example]],
    batcher: Callable[[Iterable[Example]], Iterable[List[Example]]],
    max_epochs: int,
) -> Iterable[Tuple[int, List[Example]]]:
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
