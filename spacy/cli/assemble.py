import logging
from pathlib import Path
from typing import Optional

import typer
from wasabi import msg

from .. import util
from ..util import get_sourced_components, load_model_from_config
from ._util import (
    Arg,
    Opt,
    app,
    import_code,
    parse_config_overrides,
    show_validation_error,
)


@app.command(
    "assemble",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def assemble_cli(
    # fmt: off
    ctx: typer.Context,  # This is only used to read additional arguments
    config_path: Path = Arg(..., help="Path to config file", exists=True, allow_dash=True),
    output_path: Path = Arg(..., help="Output directory to store assembled pipeline in"),
    code_path: Optional[Path] = Opt(None, "--code", "-c", help="Path to Python file with additional code (registered functions) to be imported"),
    verbose: bool = Opt(False, "--verbose", "-V", "-VV", help="Display more information for debugging purposes"),
    # fmt: on
):
    """
    Assemble a spaCy pipeline from a config file. The config file includes
    all settings for initializing the pipeline. To override settings in the
    config, e.g. settings that point to local paths or that you want to
    experiment with, you can override them as command line options. The
    --code argument lets you pass in a Python file that can be used to
    register custom functions that are referenced in the config.

    DOCS: https://spacy.io/api/cli#assemble
    """
    util.logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    # Make sure all files and paths exists if they are needed
    if not config_path or (str(config_path) != "-" and not config_path.exists()):
        msg.fail("Config file not found", config_path, exits=1)
    overrides = parse_config_overrides(ctx.args)
    import_code(code_path)
    with show_validation_error(config_path):
        config = util.load_config(config_path, overrides=overrides, interpolate=False)
    msg.divider("Initializing pipeline")
    nlp = load_model_from_config(config, auto_fill=True)
    config = config.interpolate()
    sourced = get_sourced_components(config)
    # Make sure that listeners are defined before initializing further
    nlp._link_components()
    with nlp.select_pipes(disable=[*sourced]):
        nlp.initialize()
    msg.good("Initialized pipeline")
    msg.divider("Serializing to disk")
    if output_path is not None and not output_path.exists():
        output_path.mkdir(parents=True)
        msg.good(f"Created output directory: {output_path}")
    nlp.to_disk(output_path)
