from typing import Optional, Dict, Callable, Any
import logging
from pathlib import Path
from wasabi import msg
import typer
from thinc.api import Config, fix_random_seed, set_gpu_allocator
import srsly

from .. import util
from ..util import registry, resolve_dot_names, OOV_RANK
from ..schemas import ConfigSchemaTraining, ConfigSchemaPretrain, ConfigSchemaInit
from ..language import Language
from ..lookups import Lookups
from ..errors import Errors
from ._util import init_cli, Arg, Opt, parse_config_overrides, show_validation_error
from ._util import import_code, get_sourced_components


DEFAULT_OOV_PROB = -20


@init_cli.command(
    "nlp",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
    hidden=True,
)
def init_pipeline_cli(
    # fmt: off
    ctx: typer.Context,  # This is only used to read additional arguments
    config_path: Path = Arg(..., help="Path to config file", exists=True),
    output_path: Path = Arg(..., help="Output directory for the prepared data"),
    code_path: Optional[Path] = Opt(None, "--code", "-c", help="Path to Python file with additional code (registered functions) to be imported"),
    verbose: bool = Opt(False, "--verbose", "-V", "-VV", help="Display more information for debugging purposes"),
    # fmt: on
):
    util.logger.setLevel(logging.DEBUG if verbose else logging.ERROR)
    overrides = parse_config_overrides(ctx.args)
    import_code(code_path)
    with show_validation_error(config_path):
        config = util.load_config(config_path, overrides=overrides)
    nlp = init_pipeline(config)
    nlp.to_disk(output_path)
    msg.good(f"Saved initialized pipeline to {output_path}")


def init_pipeline(config: Config, use_gpu: int = -1) -> Language:
    raw_config = config
    config = raw_config.interpolate()
    if config["training"]["seed"] is not None:
        fix_random_seed(config["training"]["seed"])
    allocator = config["training"]["gpu_allocator"]
    if use_gpu >= 0 and allocator:
        set_gpu_allocator(allocator)
    # Use original config here before it's resolved to functions
    sourced_components = get_sourced_components(config)
    with show_validation_error():
        nlp = util.load_model_from_config(raw_config, auto_fill=True)
    msg.good("Set up nlp object from config")
    config = nlp.config.interpolate()
    # Resolve all training-relevant sections using the filled nlp config
    T = registry.resolve(config["training"], schema=ConfigSchemaTraining)
    dot_names = [T["train_corpus"], T["dev_corpus"]]
    train_corpus, dev_corpus = resolve_dot_names(config, dot_names)
    I = registry.resolve(config["initialize"], schema=ConfigSchemaInit)
    V = I["vocab"]
    init_vocab(nlp, data=V["data"], lookups=V["lookups"])
    msg.good("Created vocabulary")
    if V["vectors"] is not None:
        add_vectors(nlp, V["vectors"])
        msg.good(f"Added vectors: {V['vectors']}")
    optimizer = T["optimizer"]
    before_to_disk = create_before_to_disk_callback(T["before_to_disk"])
    # Components that shouldn't be updated during training
    frozen_components = T["frozen_components"]
    # Sourced components that require resume_training
    resume_components = [p for p in sourced_components if p not in frozen_components]
    msg.info(f"Pipeline: {nlp.pipe_names}")
    if resume_components:
        with nlp.select_pipes(enable=resume_components):
            msg.info(f"Resuming training for: {resume_components}")
            nlp.resume_training(sgd=optimizer)
    with nlp.select_pipes(disable=[*frozen_components, *resume_components]):
        nlp.begin_training(lambda: train_corpus(nlp), sgd=optimizer)
        msg.good(f"Initialized pipeline components")
    # Verify the config after calling 'begin_training' to ensure labels
    # are properly initialized
    verify_config(nlp)
    if "pretraining" in config and config["pretraining"]:
        P = registry.resolve(config["pretraining"], schema=ConfigSchemaPretrain)
        add_tok2vec_weights(nlp, P, I)
    # TODO: this should be handled better?
    nlp = before_to_disk(nlp)
    return nlp


def init_vocab(
    nlp: Language, *, data: Optional[Path] = None, lookups: Optional[Lookups] = None,
) -> Language:
    if lookups:
        nlp.vocab.lookups = lookups
        msg.good(f"Added vocab lookups: {', '.join(lookups.tables)}")
    data_path = util.ensure_path(data)
    if data_path is not None:
        lex_attrs = srsly.read_jsonl(data_path)
        for lexeme in nlp.vocab:
            lexeme.rank = OOV_RANK
        for attrs in lex_attrs:
            if "settings" in attrs:
                continue
            lexeme = nlp.vocab[attrs["orth"]]
            lexeme.set_attrs(**attrs)
        if len(nlp.vocab):
            oov_prob = min(lex.prob for lex in nlp.vocab) - 1
        else:
            oov_prob = DEFAULT_OOV_PROB
        nlp.vocab.cfg.update({"oov_prob": oov_prob})
        msg.good(f"Added {len(nlp.vocab)} lexical entries to the vocab")


def add_tok2vec_weights(
    nlp: Language, pretrain_config: Dict[str, Any], vocab_config: Dict[str, Any]
) -> None:
    # Load pretrained tok2vec weights - cf. CLI command 'pretrain'
    P = pretrain_config
    V = vocab_config
    weights_data = None
    init_tok2vec = util.ensure_path(V["init_tok2vec"])
    if init_tok2vec is not None:
        if P["objective"].get("type") == "vectors" and not V["vectors"]:
            err = "Need initialize.vectors if pretraining.objective.type is vectors"
            msg.fail(err, exits=1)
        if not init_tok2vec.exists():
            msg.fail("Can't find pretrained tok2vec", init_tok2vec, exits=1)
        with init_tok2vec.open("rb") as file_:
            weights_data = file_.read()
    if weights_data is not None:
        tok2vec_component = P["component"]
        if tok2vec_component is None:
            msg.fail(
                f"To use pretrained tok2vec weights, [pretraining.component] "
                f"needs to specify the component that should load them.",
                exits=1,
            )
        layer = nlp.get_pipe(tok2vec_component).model
        if P["layer"]:
            layer = layer.get_ref(P["layer"])
        layer.from_bytes(weights_data)
        msg.good(f"Loaded pretrained weights into component '{tok2vec_component}'")


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
        msg(f"Added {len(nlp.vocab.vectors)} vectors from {vectors}")


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
