import sys
from typing import Iterable, Optional

from .static import HELP_OPTIONS, UNKNOWN_COMMAND_TOKEN, UNKNOWN_SUBCOMMAND_TOKEN
from .static import get_plugin_command_names, load_manifest


def _write_output(text: str) -> None:
    sys.stdout.write(text)
    if not text.endswith("\n"):
        sys.stdout.write("\n")


def _run_live() -> None:
    from spacy.cli import setup_cli

    setup_cli()


def _try_static(argv: Iterable[str]):
    args = list(argv)
    manifest = load_manifest()
    plugin_command_names = get_plugin_command_names()
    known_groups = manifest["known_groups"]
    known_top_level = set(manifest["known_top_level"])
    if not args:
        return manifest["errors"]["missing_command"], 2
    first = args[0]
    if first in HELP_OPTIONS:
        if plugin_command_names:
            return None
        return manifest["root_help"], 0
    if first.startswith("-"):
        return None
    if first not in known_top_level:
        if first in plugin_command_names:
            return None
        template = manifest["errors"]["unknown_command"]
        return template.replace(UNKNOWN_COMMAND_TOKEN, first), 2
    if first in known_groups:
        if len(args) == 1 or args[1] in HELP_OPTIONS:
            if plugin_command_names:
                return None
            return manifest["group_help"][first], 0
        second = args[1]
        if second not in known_groups[first]:
            if plugin_command_names:
                return None
            template = manifest["errors"]["unknown_subcommand"][first]
            return template.replace(UNKNOWN_SUBCOMMAND_TOKEN, second), 2
        if any(arg in HELP_OPTIONS for arg in args[2:]):
            return manifest["command_help"][f"{first} {second}"], 0
        return None
    if any(arg in HELP_OPTIONS for arg in args[1:]):
        return manifest["command_help"][first], 0
    return None


def main(argv: Optional[Iterable[str]] = None) -> None:
    args = sys.argv[1:] if argv is None else list(argv)
    try:
        static_result = _try_static(args)
    except Exception:
        return _run_live()
    if static_result is None:
        return _run_live()
    text, code = static_result
    _write_output(text)
    raise SystemExit(code)
