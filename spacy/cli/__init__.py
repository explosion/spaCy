import sys
import types
from importlib import import_module
from typing import Iterable

from typer.main import get_command
from wasabi import msg

from ..util import registry
from ._dispatch import (
    GROUP_MODULES,
    PUBLIC_ATTRS,
    SUBCOMMAND_MODULES,
    TOP_LEVEL_MODULES,
)
from ._dispatch import iter_builtin_modules
from ._util import COMMAND, add_project_cli, app

HELP_OPTIONS = {"--help", "-h"}
ROOT_OPTIONS = HELP_OPTIONS | {"--install-completion", "--show-completion"}

__all__ = [
    "app",
    "load_all_commands",
    "load_for_argv",
    "setup_cli",
    *sorted(PUBLIC_ATTRS),
]


def _import_modules(module_names: Iterable[str]) -> None:
    for module_name in module_names:
        import_module(module_name)


def load_all_commands() -> None:
    _import_modules(iter_builtin_modules())
    add_project_cli()


def load_for_argv(argv: Iterable[str]) -> None:
    args = list(argv)
    if not args or args[0] in ROOT_OPTIONS or args[0].startswith("-"):
        load_all_commands()
        return
    command = args[0]
    if command == "project":
        add_project_cli()
        return
    if command in GROUP_MODULES:
        subcommand = args[1] if len(args) > 1 and not args[1].startswith("-") else None
        if subcommand is not None and (command, subcommand) in SUBCOMMAND_MODULES:
            _import_modules(SUBCOMMAND_MODULES[(command, subcommand)])
            return
        _import_modules(GROUP_MODULES[command])
        return
    if command in TOP_LEVEL_MODULES:
        _import_modules(TOP_LEVEL_MODULES[command])


def setup_cli() -> None:
    # Make sure entry-point CLI integrations are imported before command dispatch.
    registry.cli.get_all()
    load_for_argv(sys.argv[1:])
    command = get_command(app)
    command(prog_name=COMMAND)


def __getattr__(name: str):
    if name not in PUBLIC_ATTRS:
        raise AttributeError(f"module 'spacy.cli' has no attribute {name!r}")
    module_name, attr_name = PUBLIC_ATTRS[name]
    module = import_module(module_name)
    value = module if attr_name is None else getattr(module, attr_name)
    globals()[name] = value
    return value


def __dir__():
    return sorted(set(globals()) | set(PUBLIC_ATTRS))


class _CLIModule(types.ModuleType):
    def __setattr__(self, name, value):
        if isinstance(value, types.ModuleType) and name in PUBLIC_ATTRS:
            _, attr_name = PUBLIC_ATTRS[name]
            if attr_name is not None:
                super().__setattr__(name, getattr(value, attr_name))
                return
        super().__setattr__(name, value)


sys.modules[__name__].__class__ = _CLIModule


@app.command("link", no_args_is_help=True, deprecated=True, hidden=True)
def link(*args, **kwargs):
    """As of spaCy v3.0, symlinks like "en" are not supported anymore. You can load trained
    pipeline packages using their full names or from a directory path."""
    msg.warn(
        "As of spaCy v3.0, model symlinks are not supported anymore. You can load trained "
        "pipeline packages using their full names or from a directory path."
    )
