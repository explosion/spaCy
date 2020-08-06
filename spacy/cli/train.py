from typing import Optional, Dict, Any, Tuple, Union, Callable, List
import srsly
import tqdm
from pathlib import Path
from wasabi import msg
import thinc
import thinc.schedules
from thinc.api import use_pytorch_for_gpu_memory, require_gpu, fix_random_seed
from thinc.api import Config, Optimizer
import random
import typer

from ._util import app, Arg, Opt, parse_config_overrides, show_validation_error
from ._util import import_code, get_sourced_components
from ..language import Language
from .. import util
from ..gold.example import Example
from ..errors import Errors


# Don't remove - required to load the built-in architectures
from ..ml import models  # noqa: F401


@app.command(
    "train", context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def train_cli(
    # fmt: off
    ctx: typer.Context,  # This is only used to read additional arguments
    config_path: Path = Arg(..., help="Path to config file", exists=True),
    output_path: Optional[Path] = Opt(None, "--output", "--output-path", "-o", help="Output directory to store model in"),
    code_path: Optional[Path] = Opt(None, "--code-path", "-c", help="Path to Python file with additional code (registered functions) to be imported"),
    verbose: bool = Opt(False, "--verbose", "-V", "-VV", help="Display more information for debugging purposes"),
    use_gpu: int = Opt(-1, "--gpu-id", "-g", help="GPU ID or -1 for CPU"),
    resume: bool = Opt(False, "--resume", "-R", help="Resume training"),
    # fmt: on
):
    """
    Train or update a spaCy model. Requires data in spaCy's binary format. To
    convert data from other formats, use the `spacy convert` command. The
    config file includes all settings and hyperparameters used during traing.
    To override settings in the config, e.g. settings that point to local
    paths or that you want to experiment with, you can override them as
    command line options. For instance, --training.batch_size 128 overrides
    the value of "batch_size" in the block "[training]". The --code argument
    lets you pass in a Python file that's imported before training. It can be
    used to register custom functions and architectures that can then be
    referenced in the config.
    """
    util.set_env_log(verbose)
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
        config = Config().from_disk(config_path, overrides=config_overrides)
    if config.get("training", {}).get("seed") is not None:
        fix_random_seed(config["training"]["seed"])
    # Use original config here before it's resolved to functions
    sourced_components = get_sourced_components(config)
    with show_validation_error(config_path):
        nlp, config = util.load_model_from_config(config)
    if config["training"]["vectors"] is not None:
        util.load_vectors_into_model(nlp, config["training"]["vectors"])
    verify_config(nlp)
    raw_text, tag_map, morph_rules, weights_data = load_from_paths(config)
    if config.get("system", {}).get("use_pytorch_for_gpu_memory"):
        # It feels kind of weird to not have a default for this.
        use_pytorch_for_gpu_memory()
    T_cfg = config["training"]
    optimizer = T_cfg["optimizer"]
    train_corpus = T_cfg["train_corpus"]
    dev_corpus = T_cfg["dev_corpus"]
    batcher = T_cfg["batcher"]
    # Components that shouldn't be updated during training
    frozen_components = T_cfg["frozen_components"]
    # Sourced components that require resume_training
    resume_components = [p for p in sourced_components if p not in frozen_components]
    msg.info(f"Pipeline: {nlp.pipe_names}")
    if resume_components:
        with nlp.select_pipes(enable=resume_components):
            msg.info(f"Resuming training for: {resume_components}")
            nlp.resume_training()
    with nlp.select_pipes(disable=[*frozen_components, *resume_components]):
        nlp.begin_training(lambda: train_corpus(nlp))

    if tag_map:
        # Replace tag map with provided mapping
        nlp.vocab.morphology.load_tag_map(tag_map)
    if morph_rules:
        # Load morph rules
        nlp.vocab.morphology.load_morph_exceptions(morph_rules)

    # Load a pretrained tok2vec model - cf. CLI command 'pretrain'
    if weights_data is not None:
        tok2vec_path = config.get("pretraining", {}).get("tok2vec_model", None)
        if tok2vec_path is None:
            msg.fail(
                f"To use a pretrained tok2vec model, the config needs to specify which "
                f"tok2vec layer to load in the setting [pretraining.tok2vec_model].",
                exits=1,
            )
        tok2vec = config
        for subpath in tok2vec_path.split("."):
            tok2vec = tok2vec.get(subpath)
        if not tok2vec:
            err = f"Could not locate the tok2vec model at {tok2vec_path}"
            msg.fail(err, exits=1)
        tok2vec.from_bytes(weights_data)

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
    print_row = setup_printer(T_cfg, nlp)

    try:
        progress = tqdm.tqdm(total=T_cfg["eval_frequency"], leave=False)
        for batch, info, is_best_checkpoint in training_step_iterator:
            progress.update(1)
            if is_best_checkpoint is not None:
                progress.close()
                print_row(info)
                if is_best_checkpoint and output_path is not None:
                    update_meta(T_cfg, nlp, info)
                    nlp.to_disk(output_path / "model-best")
                progress = tqdm.tqdm(total=T_cfg["eval_frequency"], leave=False)
    except Exception as e:
        if output_path is not None:
            msg.warn(
                f"Aborting and saving the final best model. "
                f"Encountered exception: {str(e)}",
                exits=1,
            )
        else:
            raise e
    finally:
        if output_path is not None:
            final_model_path = output_path / "model-final"
            if optimizer.averages:
                with nlp.use_params(optimizer.averages):
                    nlp.to_disk(final_model_path)
            else:
                nlp.to_disk(final_model_path)
            msg.good(f"Saved model to output directory {final_model_path}")


def create_train_batches(iterator, batcher, max_epochs: int):
    epoch = 1
    examples = []
    # Stream the first epoch, so we start training faster and support
    # infinite streams.
    for batch in batcher(iterator):
        yield epoch, batch
        if max_epochs != 1:
            examples.extend(batch)
    if not examples:
        # Raise error if no data
        raise ValueError(Errors.E986)
    while epoch != max_epochs:
        random.shuffle(examples)
        for batch in batcher(examples):
            yield epoch, batch
        epoch += 1


def create_evaluation_callback(
    nlp: Language, dev_corpus: Callable, weights: Dict[str, float],
) -> Callable[[], Tuple[float, Dict[str, float]]]:
    def evaluate() -> Tuple[float, Dict[str, float]]:
        dev_examples = list(dev_corpus(nlp))
        scores = nlp.evaluate(dev_examples)
        # Calculate a weighted sum based on score_weights for the main score
        try:
            weighted_score = sum(scores[s] * weights.get(s, 0.0) for s in weights)
        except KeyError as e:
            keys = list(scores.keys())
            err = Errors.E983.format(dict="score_weights", key=str(e), keys=keys)
            raise KeyError(err) from None
        return weighted_score, scores

    return evaluate


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
    The evaluation is conducted by calling the evaluate callback, which should

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
        score (float): The main score form the last evaluation.
        other_scores: : The other scores from the last evaluation.
        loss: The accumulated losses throughout training.
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
            if name not in exclude and hasattr(proc, "model"):
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
        info = {
            "epoch": epoch,
            "step": step,
            "score": score,
            "other_scores": other_scores,
            "losses": losses,
            "checkpoints": results,
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


def setup_printer(
    training: Union[Dict[str, Any], Config], nlp: Language
) -> Callable[[Dict[str, Any]], None]:
    score_cols = list(training["score_weights"])
    score_widths = [max(len(col), 6) for col in score_cols]
    loss_cols = [f"Loss {pipe}" for pipe in nlp.pipe_names]
    loss_widths = [max(len(col), 8) for col in loss_cols]
    table_header = ["E", "#"] + loss_cols + score_cols + ["Score"]
    table_header = [col.upper() for col in table_header]
    table_widths = [3, 6] + loss_widths + score_widths + [6]
    table_aligns = ["r" for _ in table_widths]
    msg.row(table_header, widths=table_widths)
    msg.row(["-" * width for width in table_widths])

    def print_row(info: Dict[str, Any]) -> None:
        try:
            losses = [
                "{0:.2f}".format(float(info["losses"][pipe_name]))
                for pipe_name in nlp.pipe_names
            ]
        except KeyError as e:
            raise KeyError(
                Errors.E983.format(
                    dict="scores (losses)", key=str(e), keys=list(info["losses"].keys())
                )
            ) from None

        try:
            scores = [
                "{0:.2f}".format(float(info["other_scores"][col])) for col in score_cols
            ]
        except KeyError as e:
            raise KeyError(
                Errors.E983.format(
                    dict="scores (other)",
                    key=str(e),
                    keys=list(info["other_scores"].keys()),
                )
            ) from None
        data = (
            [info["epoch"], info["step"]]
            + losses
            + scores
            + ["{0:.2f}".format(float(info["score"]))]
        )
        msg.row(data, widths=table_widths, aligns=table_aligns)

    return print_row


def update_meta(
    training: Union[Dict[str, Any], Config], nlp: Language, info: Dict[str, Any]
) -> None:
    nlp.meta["performance"] = {}
    for metric in training["score_weights"]:
        nlp.meta["performance"][metric] = info["other_scores"][metric]
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


def verify_cli_args(config_path: Path, output_path: Optional[Path] = None,) -> None:
    # Make sure all files and paths exists if they are needed
    if not config_path or not config_path.exists():
        msg.fail("Config file not found", config_path, exits=1)
    if output_path is not None:
        if not output_path.exists():
            output_path.mkdir()
            msg.good(f"Created output directory: {output_path}")
        elif output_path.exists() and [p for p in output_path.iterdir() if p.is_dir()]:
            msg.warn(
                "Output directory is not empty.",
                "This can lead to unintended side effects when saving the model. "
                "Please use an empty directory or a different path instead. If "
                "the specified output path doesn't exist, the directory will be "
                "created for you.",
            )


def verify_config(nlp: Language) -> None:
    """Perform additional checks based on the config and loaded nlp object."""
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
        textcat_labels = nlp.get_pipe("textcat").cfg.get("labels", [])
        pos_label = pipe_config.get("positive_label")
        if pos_label not in textcat_labels:
            msg.fail(
                f"The textcat's 'positive_label' config setting '{pos_label}' "
                f"does not match any label in the training data.",
                exits=1,
            )
        if len(textcat_labels) != 2:
            msg.fail(
                f"A textcat 'positive_label' '{pos_label}' was "
                f"provided for training data that does not appear to be a "
                f"binary classification problem with two labels.",
                exits=1,
            )
