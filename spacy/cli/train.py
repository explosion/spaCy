from typing import Optional, Dict, Any, Tuple, Union, Callable, List
from timeit import default_timer as timer
import srsly
import tqdm
from pathlib import Path
from wasabi import msg
import thinc
import thinc.schedules
from thinc.api import Config, Optimizer, require_gpu, fix_random_seed, set_gpu_allocator
import random
import typer
import logging

from ._util import app, Arg, Opt, parse_config_overrides, show_validation_error
from ._util import import_code, get_sourced_components
from ..language import Language
from .. import util
from ..training.example import Example
from ..errors import Errors
from ..util import dot_to_object


@app.command(
    "train", context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def train_cli(
    # fmt: off
    ctx: typer.Context,  # This is only used to read additional arguments
    config_path: Path = Arg(..., help="Path to config file", exists=True),
    output_path: Optional[Path] = Opt(None, "--output", "--output-path", "-o", help="Output directory to store trained pipeline in"),
    code_path: Optional[Path] = Opt(None, "--code", "-c", help="Path to Python file with additional code (registered functions) to be imported"),
    verbose: bool = Opt(False, "--verbose", "-V", "-VV", help="Display more information for debugging purposes"),
    use_gpu: int = Opt(-1, "--gpu-id", "-g", help="GPU ID or -1 for CPU"),
    resume: bool = Opt(False, "--resume", "-R", help="Resume training"),
    # fmt: on
):
    """
    Train or update a spaCy pipeline. Requires data in spaCy's binary format. To
    convert data from other formats, use the `spacy convert` command. The
    config file includes all settings and hyperparameters used during traing.
    To override settings in the config, e.g. settings that point to local
    paths or that you want to experiment with, you can override them as
    command line options. For instance, --training.batch_size 128 overrides
    the value of "batch_size" in the block "[training]". The --code argument
    lets you pass in a Python file that's imported before training. It can be
    used to register custom functions and architectures that can then be
    referenced in the config.

    DOCS: https://nightly.spacy.io/api/cli#train
    """
    util.logger.setLevel(logging.DEBUG if verbose else logging.ERROR)
    verify_cli_args(config_path, output_path)
    overrides = parse_config_overrides(ctx.args)
    import_code(code_path)
    train(
        config_path,
        output_path=output_path,
        config_overrides=overrides,
        use_gpu=use_gpu,
        resume_training=resume,
    )


def train(
    config_path: Path,
    output_path: Optional[Path] = None,
    config_overrides: Dict[str, Any] = {},
    use_gpu: int = -1,
    resume_training: bool = False,
) -> None:
    if use_gpu >= 0:
        msg.info(f"Using GPU: {use_gpu}")
        require_gpu(use_gpu)
    else:
        msg.info("Using CPU")
    msg.info(f"Loading config and nlp from: {config_path}")
    with show_validation_error(config_path):
        config = util.load_config(
            config_path, overrides=config_overrides, interpolate=True
        )
        # Keep a second un-interpolated config so we can preserve variables in
        # the final nlp object we train and serialize
        raw_config = util.load_config(config_path, overrides=config_overrides)
    if config["training"]["seed"] is not None:
        fix_random_seed(config["training"]["seed"])
    allocator = config["training"]["gpu_allocator"]
    if use_gpu >= 0 and allocator:
        set_gpu_allocator(allocator)
    # Use original config here before it's resolved to functions
    sourced_components = get_sourced_components(config)
    with show_validation_error(config_path):
        nlp, config = util.load_model_from_config(raw_config)
    util.load_vocab_data_into_model(nlp, lookups=config["training"]["lookups"])
    if config["training"]["vectors"] is not None:
        add_vectors(nlp, config["training"]["vectors"])
    raw_text, tag_map, morph_rules, weights_data = load_from_paths(config)
    T_cfg = config["training"]
    optimizer = T_cfg["optimizer"]
    train_corpus = dot_to_object(config, T_cfg["train_corpus"])
    dev_corpus = dot_to_object(config, T_cfg["dev_corpus"])
    batcher = T_cfg["batcher"]
    train_logger = T_cfg["logger"]
    before_to_disk = create_before_to_disk_callback(T_cfg["before_to_disk"])
    # Components that shouldn't be updated during training
    frozen_components = T_cfg["frozen_components"]
    # Sourced components that require resume_training
    resume_components = [p for p in sourced_components if p not in frozen_components]
    msg.info(f"Pipeline: {nlp.pipe_names}")
    if resume_components:
        with nlp.select_pipes(enable=resume_components):
            msg.info(f"Resuming training for: {resume_components}")
            nlp.resume_training(sgd=optimizer)
    with nlp.select_pipes(disable=[*frozen_components, *resume_components]):
        nlp.begin_training(lambda: train_corpus(nlp), sgd=optimizer)
    # Verify the config after calling 'begin_training' to ensure labels are properly initialized
    verify_config(nlp)

    if tag_map:
        # Replace tag map with provided mapping
        nlp.vocab.morphology.load_tag_map(tag_map)
    if morph_rules:
        # Load morph rules
        nlp.vocab.morphology.load_morph_exceptions(morph_rules)

    # Load pretrained tok2vec weights - cf. CLI command 'pretrain'
    if weights_data is not None:
        tok2vec_component = config["pretraining"]["component"]
        if tok2vec_component is None:
            msg.fail(
                f"To use pretrained tok2vec weights, [pretraining.component] "
                f"needs to specify the component that should load them.",
                exits=1,
            )
        layer = nlp.get_pipe(tok2vec_component).model
        tok2vec_layer = config["pretraining"]["layer"]
        if tok2vec_layer:
            layer = layer.get_ref(tok2vec_layer)
        layer.from_bytes(weights_data)
        msg.info(f"Loaded pretrained weights into component '{tok2vec_component}'")

    # Create iterator, which yields out info after each optimization step.
    msg.info("Start training")
    score_weights = T_cfg["score_weights"]
    training_step_iterator = train_while_improving(
        nlp,
        optimizer,
        create_train_batches(train_corpus(nlp), batcher, T_cfg["max_epochs"]),
        create_evaluation_callback(nlp, dev_corpus, score_weights),
        dropout=T_cfg["dropout"],
        accumulate_gradient=T_cfg["accumulate_gradient"],
        patience=T_cfg["patience"],
        max_steps=T_cfg["max_steps"],
        eval_frequency=T_cfg["eval_frequency"],
        raw_text=None,
        exclude=frozen_components,
    )
    msg.info(f"Training. Initial learn rate: {optimizer.learn_rate}")
    with nlp.select_pipes(disable=frozen_components):
        print_row, finalize_logger = train_logger(nlp)

    try:
        progress = tqdm.tqdm(total=T_cfg["eval_frequency"], leave=False)
        progress.set_description(f"Epoch 1")
        for batch, info, is_best_checkpoint in training_step_iterator:
            progress.update(1)
            if is_best_checkpoint is not None:
                progress.close()
                print_row(info)
                if is_best_checkpoint and output_path is not None:
                    with nlp.select_pipes(disable=frozen_components):
                        update_meta(T_cfg, nlp, info)
                    with nlp.use_params(optimizer.averages):
                        nlp = before_to_disk(nlp)
                        nlp.to_disk(output_path / "model-best")
                progress = tqdm.tqdm(total=T_cfg["eval_frequency"], leave=False)
                progress.set_description(f"Epoch {info['epoch']}")
    except Exception as e:
        finalize_logger()
        if output_path is not None:
            # We don't want to swallow the traceback if we don't have a
            # specific error.
            msg.warn(
                f"Aborting and saving the final best model. "
                f"Encountered exception: {str(e)}"
            )
            nlp = before_to_disk(nlp)
            nlp.to_disk(output_path / "model-final")
        raise e
    finally:
        finalize_logger()
        if output_path is not None:
            final_model_path = output_path / "model-final"
            if optimizer.averages:
                with nlp.use_params(optimizer.averages):
                    nlp.to_disk(final_model_path)
            else:
                nlp.to_disk(final_model_path)
            msg.good(f"Saved pipeline to output directory {final_model_path}")


def add_vectors(nlp: Language, vectors: str) -> None:
    title = f"Config validation error for vectors {vectors}"
    desc = (
        "This typically means that there's a problem in the config.cfg included "
        "with the packaged vectors. Make sure that the vectors package you're "
        "loading is compatible with the current version of spaCy."
    )
    with show_validation_error(
        title=title, desc=desc, hint_fill=False, show_config=False
    ):
        util.load_vectors_into_model(nlp, vectors)


def create_train_batches(iterator, batcher, max_epochs: int):
    epoch = 0
    examples = list(iterator)
    if not examples:
        # Raise error if no data
        raise ValueError(Errors.E986)
    while max_epochs < 1 or epoch != max_epochs:
        random.shuffle(examples)
        for batch in batcher(examples):
            yield epoch, batch
        epoch += 1


def create_evaluation_callback(
    nlp: Language, dev_corpus: Callable, weights: Dict[str, float]
) -> Callable[[], Tuple[float, Dict[str, float]]]:
    weights = {key: value for key, value in weights.items() if value is not None}

    def evaluate() -> Tuple[float, Dict[str, float]]:
        dev_examples = list(dev_corpus(nlp))
        scores = nlp.evaluate(dev_examples)
        # Calculate a weighted sum based on score_weights for the main score.
        # We can only consider scores that are ints/floats, not dicts like
        # entity scores per type etc.
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


def create_before_to_disk_callback(
    callback: Optional[Callable[[Language], Language]]
) -> Callable[[Language], Language]:
    def before_to_disk(nlp: Language) -> Language:
        if not callback:
            return nlp
        modified_nlp = callback(nlp)
        if not isinstance(modified_nlp, Language):
            err = Errors.E914.format(name="before_to_disk", value=type(modified_nlp))
            raise ValueError(err)
        return modified_nlp

    return before_to_disk


def train_while_improving(
    nlp: Language,
    optimizer: Optimizer,
    train_data,
    evaluate,
    *,
    dropout: float,
    eval_frequency: int,
    accumulate_gradient: int,
    patience: int,
    max_steps: int,
    raw_text: List[Dict[str, str]],
    exclude: List[str],
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
        dropouts = thinc.schedules.constant(dropout)
    else:
        dropouts = dropout
    results = []
    losses = {}
    if raw_text:
        random.shuffle(raw_text)
        raw_examples = [
            Example.from_dict(nlp.make_doc(rt["text"]), {}) for rt in raw_text
        ]
        raw_batches = util.minibatch(raw_examples, size=8)

    words_seen = 0
    start_time = timer()
    for step, (epoch, batch) in enumerate(train_data):
        dropout = next(dropouts)
        for subbatch in subdivide_batch(batch, accumulate_gradient):

            nlp.update(
                subbatch, drop=dropout, losses=losses, sgd=False, exclude=exclude
            )
            if raw_text:
                # If raw text is available, perform 'rehearsal' updates,
                # which use unlabelled data to reduce overfitting.
                raw_batch = list(next(raw_batches))
                nlp.rehearse(raw_batch, sgd=optimizer, losses=losses, exclude=exclude)
        # TODO: refactor this so we don't have to run it separately in here
        for name, proc in nlp.pipeline:
            if (
                name not in exclude
                and hasattr(proc, "model")
                and proc.model not in (True, False, None)
            ):
                proc.model.finish_update(optimizer)
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
        best_score, best_step = max(results)
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


def update_meta(
    training: Union[Dict[str, Any], Config], nlp: Language, info: Dict[str, Any]
) -> None:
    nlp.meta["performance"] = {}
    for metric in training["score_weights"]:
        if metric is not None:
            nlp.meta["performance"][metric] = info["other_scores"].get(metric, 0.0)
    for pipe_name in nlp.pipe_names:
        nlp.meta["performance"][f"{pipe_name}_loss"] = info["losses"][pipe_name]


def load_from_paths(
    config: Config,
) -> Tuple[List[Dict[str, str]], Dict[str, dict], bytes]:
    # TODO: separate checks from loading
    raw_text = util.ensure_path(config["training"]["raw_text"])
    if raw_text is not None:
        if not raw_text.exists():
            msg.fail("Can't find raw text", raw_text, exits=1)
        raw_text = list(srsly.read_jsonl(config["training"]["raw_text"]))
    tag_map = {}
    morph_rules = {}
    weights_data = None
    init_tok2vec = util.ensure_path(config["training"]["init_tok2vec"])
    if init_tok2vec is not None:
        if not init_tok2vec.exists():
            msg.fail("Can't find pretrained tok2vec", init_tok2vec, exits=1)
        with init_tok2vec.open("rb") as file_:
            weights_data = file_.read()
    return raw_text, tag_map, morph_rules, weights_data


def verify_cli_args(config_path: Path, output_path: Optional[Path] = None) -> None:
    # Make sure all files and paths exists if they are needed
    if not config_path or not config_path.exists():
        msg.fail("Config file not found", config_path, exits=1)
    if output_path is not None:
        if not output_path.exists():
            output_path.mkdir()
            msg.good(f"Created output directory: {output_path}")


def verify_config(nlp: Language) -> None:
    """Perform additional checks based on the config, loaded nlp object and training data."""
    # TODO: maybe we should validate based on the actual components, the list
    # in config["nlp"]["pipeline"] instead?
    for pipe_config in nlp.config["components"].values():
        # We can't assume that the component name == the factory
        factory = pipe_config["factory"]
        if factory == "textcat":
            verify_textcat_config(nlp, pipe_config)


def verify_textcat_config(nlp: Language, pipe_config: Dict[str, Any]) -> None:
    # if 'positive_label' is provided: double check whether it's in the data and
    # the task is binary
    if pipe_config.get("positive_label"):
        textcat_labels = nlp.get_pipe("textcat").labels
        pos_label = pipe_config.get("positive_label")
        if pos_label not in textcat_labels:
            raise ValueError(
                Errors.E920.format(pos_label=pos_label, labels=textcat_labels)
            )
        if len(list(textcat_labels)) != 2:
            raise ValueError(
                Errors.E919.format(pos_label=pos_label, labels=textcat_labels)
            )
