from typing import Optional, List
from pathlib import Path
from wasabi import msg
import logging
from radicli import Arg, ExistingFilePathOrDash, ExistingFilePath

from ._util import cli, parse_config_overrides, show_validation_error
from ._util import import_code
from .. import util
from ..util import get_sourced_components, load_model_from_config


@cli.command_with_extra(
    "assemble",
    # fmt: off
    config_path=Arg(help="Path to config file"),
    output_path=Arg(help="Output directory to store assembled pipeline in"),
    code_path=Arg("--code", "-c", help="Path to Python file with additional code (registered functions) to be imported"),
    verbose=Arg("--verbose", "-V", help="Display more information for debugging purposes"),
    # fmt: on
)
def assemble_cli(
    config_path: ExistingFilePathOrDash,
    output_path: Optional[Path] = None,
    code_path: Optional[ExistingFilePath] = None,
    verbose: bool = False,
    _extra: List[str] = [],
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
    overrides = parse_config_overrides(_extra)
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
