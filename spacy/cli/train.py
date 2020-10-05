from typing import Optional
from pathlib import Path
from wasabi import msg
import typer
import logging
import sys

from ._util import app, Arg, Opt, parse_config_overrides, show_validation_error
from ._util import import_code, setup_gpu
from ..training.loop import train
from ..training.initialize import init_nlp
from .. import util


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
    use_gpu: int = Opt(-1, "--gpu-id", "-g", help="GPU ID or -1 for CPU")
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
    util.logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    # Make sure all files and paths exists if they are needed
    if not config_path or not config_path.exists():
        msg.fail("Config file not found", config_path, exits=1)
    if output_path is not None and not output_path.exists():
        output_path.mkdir()
        msg.good(f"Created output directory: {output_path}")
    overrides = parse_config_overrides(ctx.args)
    import_code(code_path)
    setup_gpu(use_gpu)
    with show_validation_error(config_path):
        config = util.load_config(config_path, overrides=overrides, interpolate=False)
    msg.divider("Initializing pipeline")
    with show_validation_error(config_path, hint_fill=False):
        nlp = init_nlp(config, use_gpu=use_gpu)
    msg.good("Initialized pipeline")
    msg.divider("Training pipeline")
    train(nlp, output_path, use_gpu=use_gpu, stdout=sys.stdout, stderr=sys.stderr)
