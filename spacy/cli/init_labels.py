from typing import Optional
import logging
from pathlib import Path
from wasabi import msg
import typer
import srsly

from .. import util
from ..training.initialize import init_nlp, convert_vectors
from ._util import init_cli, Arg, Opt, parse_config_overrides, show_validation_error
from ._util import import_code, setup_gpu


@init_cli.command(
    "labels",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def init_labels_cli(
    # fmt: off
    ctx: typer.Context,  # This is only used to read additional arguments
    config_path: Path = Arg(..., help="Path to config file", exists=True),
    output_path: Path = Arg(..., help="Output directory for the labels"),
    code_path: Optional[Path] = Opt(None, "--code", "-c", help="Path to Python file with additional code (registered functions) to be imported"),
    verbose: bool = Opt(False, "--verbose", "-V", "-VV", help="Display more information for debugging purposes"),
    use_gpu: int = Opt(-1, "--gpu-id", "-g", help="GPU ID or -1 for CPU")
    # fmt: on
):
    if not output_path.exists():
        output_path.mkdir()
    util.logger.setLevel(logging.DEBUG if verbose else logging.ERROR)
    overrides = parse_config_overrides(ctx.args)
    import_code(code_path)
    setup_gpu(use_gpu)
    with show_validation_error(config_path):
        config = util.load_config(config_path, overrides=overrides)
    with show_validation_error(hint_fill=False):
        nlp = init_nlp(config, use_gpu=use_gpu, silent=False)
    for name, component in nlp.pipeline:
        if getattr(component, "label_data", None) is not None:
            srsly.write_json(output_path / f"{name}.json", component.label_data)
            msg.good(f"Saving {name} labels to {output_path}/{name}.json")
        else:
            msg.info(f"No labels found for {name}")
