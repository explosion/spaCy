from typing import Optional, Dict, Any, Tuple, Union, Callable, List
import logging
import srsly
from pathlib import Path
from wasabi import msg
import typer
from thinc.api import Config, fix_random_seed

from .train import create_before_to_disk_callback
from .. import util
from ..util import registry
from ..schemas import ConfigSchemaTraining
from ._util import init_cli, Arg, Opt, parse_config_overrides, show_validation_error
from ._util import import_code, get_sourced_components
from ..util import resolve_dot_names


@init_cli.command(
    "pipeline",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
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
    config = util.load_config(config_path, overrides=overrides)
    with show_validation_error(config_path):
        nlp = init_pipeline(config)
    nlp.to_disk(output_path)


def must_initialize(init_path: Path, config_path: Path, overrides: Dict) -> bool:
    config = util.load_config(config_path, overrides=overrides)
    if not init_path.exists():
        return True
    elif not (init_path / "config.cfg").exists():
        return True
    else:
        init_cfg = util.load_config(init_path / "config.cfg", interpolate=True)
        if config.to_str() != init_cfg.to_str():
            return True
        else:
            return False


def init_pipeline(config: Config, use_gpu=-1):
    raw_config = config
    config = raw_config.interpolate()
    if config["training"]["seed"] is not None:
        fix_random_seed(config["training"]["seed"])
    allocator = config["training"]["gpu_allocator"]
    if use_gpu >= 0 and allocator:
        set_gpu_allocator(allocator)
    # Use original config here before it's resolved to functions
    sourced_components = get_sourced_components(config)
    nlp = util.load_model_from_config(raw_config)
    # Resolve all training-relevant sections using the filled nlp config
    T = registry.resolve(
        config["training"],
        schema=ConfigSchemaTraining,
        validate=True,
    )
    dot_names = [T["train_corpus"], T["dev_corpus"], T["raw_text"]]
    train_corpus, dev_corpus, raw_text = resolve_dot_names(config, dot_names)
    util.load_vocab_data_into_model(nlp, lookups=T["lookups"])
    if T["vectors"] is not None:
        add_vectors(nlp, T["vectors"])
    score_weights = T["score_weights"]
    optimizer = T["optimizer"]
    batcher = T["batcher"]
    train_logger = T["logger"]
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
    # Verify the config after calling 'begin_training' to ensure labels
    # are properly initialized
    verify_config(nlp)

    # Load pretrained tok2vec weights - cf. CLI command 'pretrain'
    if weights_data is not None:
        tok2vec_component = C["pretraining"]["component"]
        if tok2vec_component is None:
            msg.fail(
                f"To use pretrained tok2vec weights, [pretraining.component] "
                f"needs to specify the component that should load them.",
                exits=1,
            )
        layer = nlp.get_pipe(tok2vec_component).model
        tok2vec_layer = C["pretraining"]["layer"]
        if tok2vec_layer:
            layer = layer.get_ref(tok2vec_layer)
        layer.from_bytes(weights_data)
        msg.info(f"Loaded pretrained weights into component '{tok2vec_component}'")
    return nlp
