import json
from pathlib import Path
from typing import Dict, Iterable, List

from typer.main import get_command
from typer.testing import CliRunner

from spacy.cli import load_all_commands
from spacy.cli._util import COMMAND, app

from .static import MANIFEST_FILE, UNKNOWN_COMMAND_TOKEN, UNKNOWN_SUBCOMMAND_TOKEN

DEFAULT_ENV = {"COLUMNS": "100", "LINES": "40", "TERM": "xterm-256color"}


def _invoke(runner: CliRunner, cli, args: Iterable[str]):
    return runner.invoke(cli, list(args), prog_name=COMMAND, env=DEFAULT_ENV)


def _get_help(runner: CliRunner, cli, args: Iterable[str]) -> str:
    result = _invoke(runner, cli, [*list(args), "--help"])
    if result.exit_code != 0:
        err = f"Could not render help for: {' '.join(args) or '<root>'}"
        raise RuntimeError(err)
    return result.stdout


def _maybe_get_help(runner: CliRunner, cli, args: Iterable[str]):
    result = _invoke(runner, cli, [*list(args), "--help"])
    if result.exit_code != 0:
        return None
    return result.stdout


def build_manifest() -> Dict[str, object]:
    load_all_commands()
    cli = get_command(app)
    runner = CliRunner()
    known_top_level: List[str] = sorted(cli.commands.keys())
    known_groups: Dict[str, List[str]] = {}
    hidden_top_level: List[str] = []
    hidden_group_commands: Dict[str, List[str]] = {}
    group_help: Dict[str, str] = {}
    command_help: Dict[str, str] = {}
    unknown_subcommand: Dict[str, str] = {}

    for name, command in cli.commands.items():
        if getattr(command, "hidden", False):
            hidden_top_level.append(name)
        if hasattr(command, "commands"):
            subcommands = sorted(command.commands.keys())
            known_groups[name] = subcommands
            hidden_group_commands[name] = sorted(
                sub_name
                for sub_name, sub_cmd in command.commands.items()
                if getattr(sub_cmd, "hidden", False)
            )
            group_help[name] = _get_help(runner, app, [name])
            unknown_subcommand[name] = _invoke(
                runner, app, [name, UNKNOWN_SUBCOMMAND_TOKEN]
            ).output
            for sub_name in subcommands:
                help_text = _maybe_get_help(runner, app, [name, sub_name])
                if help_text is not None:
                    command_help[f"{name} {sub_name}"] = help_text
        else:
            command_help[name] = _get_help(runner, app, [name])

    return {
        "command": COMMAND,
        "known_top_level": known_top_level,
        "known_groups": known_groups,
        "hidden_top_level": hidden_top_level,
        "hidden_group_commands": hidden_group_commands,
        "root_help": _get_help(runner, app, []),
        "group_help": group_help,
        "command_help": command_help,
        "errors": {
            "missing_command": _invoke(runner, app, []).output,
            "unknown_command": _invoke(runner, app, [UNKNOWN_COMMAND_TOKEN]).output,
            "unknown_subcommand": unknown_subcommand,
        },
    }


def write_manifest(path: Path) -> Path:
    data = build_manifest()
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    )
    return path


def main() -> None:
    write_manifest(Path(__file__).with_name(MANIFEST_FILE))


if __name__ == "__main__":
    main()
