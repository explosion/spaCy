from typing import Optional
from wasabi import Printer, diff_strings, MarkdownRenderer
from pathlib import Path
from radicli import Arg, ExistingFilePathOrDash, ExistingFilePath

from ._util import cli, show_validation_error
from .init_config import init_config, OptimizationsType
from ..util import load_config


@cli.subcommand(
    "debug",
    "diff-config",
    # fmt: off
    config_path=Arg(help="Path to config file"),
    compare_to=Arg(help="Path to a config file to diff against, or `None` to compare against default settings"),
    optimize=Arg("--optimize", "-o", help="Whether the user config was optimized for efficiency or accuracy. Only relevant when comparing against the default config"),
    gpu=Arg("--gpu", "-G", help="Whether the original config can run on a GPU. Only relevant when comparing against the default config"),
    pretraining=Arg("--pretraining", "--pt", help="Whether to compare on a config with pretraining involved. Only relevant when comparing against the default config"),
    markdown=Arg("--markdown", "-md", help="Generate Markdown for GitHub issues"),
    # fmt: on
)
def debug_diff_cli(
    config_path: ExistingFilePathOrDash,
    compare_to: Optional[ExistingFilePath] = None,
    optimize: OptimizationsType = "efficiency",
    gpu: bool = False,
    pretraining: bool = False,
    markdown: bool = False,
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
    optimize: OptimizationsType,
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
                optimize=optimize,
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
