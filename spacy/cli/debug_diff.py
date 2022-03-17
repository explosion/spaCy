from typing import Optional

import typer
from wasabi import Printer, diff_strings
from pathlib import Path
from thinc.api import Config

from ._util import debug_cli, Arg, Opt, show_validation_error, parse_config_overrides
from ..util import load_config
from .init_config import init_config, Optimizations


@debug_cli.command(
    "diff",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def debug_diff_cli(
    # fmt: off
    ctx: typer.Context,
    config_path: Path = Arg(..., help="Path to config file", exists=True, allow_dash=True),
    compare_to: Optional[Path] = Opt(None, help="Path to another config file to diff against", exists=True, allow_dash=True),
    optimize: Optimizations = Opt(Optimizations.efficiency.value, "--optimize", "-o", help="Whether the user config was optimized for efficiency or accuracy."),
    gpu: bool = Opt(False, "--gpu", "-G", help="Whether the original config can run on a GPU"),
    pretraining: bool = Opt(False, "--pretraining", "--pt", help="Whether to compare on a config with pretraining involved")
    # fmt: on
):
    """Show a diff of a config file with respect to a default configuration."""
    debug_diff(
        config_path=config_path,
        compare_to=compare_to,
        gpu=gpu,
        optimize=optimize,
        pretraining=pretraining,
    )


def debug_diff(
    config_path: Path,
    compare_to: Optional[Path],
    gpu: bool,
    optimize: Optimizations,
    pretraining: bool,
):
    msg = Printer()
    with show_validation_error(hint_fill=False):
        user_config = load_config(config_path)
        if compare_to:
            other_config = load_config(compare_to)
        else:
            # Recreate a default config based from user's config
            lang = user_config["nlp"]["lang"]
            pipeline = list(user_config["nlp"]["pipeline"])
            msg.info(f"Found user-defined language: '{lang}'")
            msg.info(f"Found user-defined pipelines: {pipeline}")
            other_config = init_config(
                lang=lang,
                pipeline=pipeline,
                optimize=optimize.value,
                gpu=gpu,
                pretraining=pretraining,
                silent=True,
            )

    user = user_config.to_str()
    other = other_config.to_str()
    if user == other:
        msg.warn("No diff to show: configs are identical")
    else:
        print(diff_strings(user, other))
