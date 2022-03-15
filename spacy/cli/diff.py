from typing import Optional
from wasabi import Printer, diff_strings
from pathlib import Path
from thinc.api import Config

from ._util import debug_cli, Arg, Opt, show_validation_error
from ..util import load_config
from ..cli.init_config import init_config, Optimizations


@debug_cli.command("diff")
def diff_config(
    # fmt: off
    config_path: Path = Arg(..., help="Path to config file", exists=True, allow_dash=True),
    compare_to: Optional[Path] = Opt(..., help="Path to another config file to diff against", exists=True, allow_dash=True),
    optimize: Optimizations = Opt(Optimizations.efficiency.value, "--optimize", "-o", help="Whether the user config was optimized for efficiency or accuracy."),
    pretraining: bool = Opt(False, "--pretraining", "--pt", help="Whether to compare on a config with pretraining involved")
    # fmt: on
):
    msg = Printer()
    with show_validation_error(hint_fill=False):
        user_config = load_config(config_path)
        # Attempt to recreate a default config based from user-defined input
        if compare_to:
            other_config = load_config(compare_to)
        else:
            other_config = init_config(
                optimize=optimize.value,
                lang=list(user_config["nlp"]["lang"]),
                pipeline=list(user_config["nlp"]["pipeline"]),
                pretraining=pretraining,
                silent=True,
            )

    user = user_config.to_str()
    other = other_config.to_str()

    if user == other:
        msg.warn("No diff to show: configs are identical")
    print(diff_strings(user, other))
