from pathlib import Path
from typing import Optional

import typer
from thinc.api import Config
from wasabi import MarkdownRenderer, Printer, diff_strings

from ..util import load_config
from ._util import Arg, Opt, debug_cli, parse_config_overrides, show_validation_error
from .init_config import Optimizations, init_config


@debug_cli.command(
    "diff-config",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def debug_diff_cli(
    # fmt: off
    ctx: typer.Context,
    config_path: Path = Arg(..., help="Path to config file", exists=True, allow_dash=True),
    compare_to: Optional[Path] = Opt(None, help="Path to a config file to diff against, or `None` to compare against default settings", exists=True, allow_dash=True),
    optimize: Optimizations = Opt(Optimizations.efficiency.value, "--optimize", "-o", help="Whether the user config was optimized for efficiency or accuracy. Only relevant when comparing against the default config."),
    gpu: bool = Opt(False, "--gpu", "-G", help="Whether the original config can run on a GPU. Only relevant when comparing against the default config."),
    pretraining: bool = Opt(False, "--pretraining", "--pt", help="Whether to compare on a config with pretraining involved. Only relevant when comparing against the default config."),
    markdown: bool = Opt(False, "--markdown", "-md", help="Generate Markdown for GitHub issues")
    # fmt: on
):
    """Show a diff of a config file with respect to spaCy's defaults or another config file. If
    additional settings were used in the creation of the config file, then you
    must supply these as extra parameters to the command when comparing to the default settings. The generated diff
    can also be used when posting to the discussion forum to provide more
    information for the maintainers.

    The `optimize`, `gpu`, and `pretraining` options are only relevant when
    comparing against the default configuration (or specifically when `compare_to` is None).

    DOCS: https://spacy.io/api/cli#debug-diff
    """
    debug_diff(
        config_path=config_path,
        compare_to=compare_to,
        gpu=gpu,
        optimize=optimize,
        pretraining=pretraining,
        markdown=markdown,
    )


def debug_diff(
    config_path: Path,
    compare_to: Optional[Path],
    gpu: bool,
    optimize: Optimizations,
    pretraining: bool,
    markdown: bool,
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
        diff_text = diff_strings(other, user, add_symbols=markdown)
        if markdown:
            md = MarkdownRenderer()
            md.add(md.code_block(diff_text, "diff"))
            print(md.text)
        else:
            print(diff_text)
