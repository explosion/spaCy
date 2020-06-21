from typing import List, Dict
import typer
import srsly
from pathlib import Path
import os
import subprocess
import sys
from wasabi import msg
import shlex

from ._app import app, Arg, Opt
from .. import about
from ..schemas import ProjectConfigSchema, validate

CONFIG_FILE = "project.yml"
SUBDIRS = [
    "assets",
    "configs",
    "packages",
    "metrics",
    "scripts",
    "notebooks",
    "training",
]


project_cli = typer.Typer(help="Command-line interface for spaCy projects")


def load_project_config(path):
    config_path = path / CONFIG_FILE
    if not config_path.exists():
        msg.fail("Can't find project config", config_path, exits=1)
    config = srsly.read_yaml(config_path)
    errors = validate(ProjectConfigSchema, config)
    if errors:
        msg.fail(f"Invalid project config in {CONFIG_FILE}", "\n".join(errors), exits=1)
    return config


def create_dirs(project_dir: Path):
    for subdir in SUBDIRS:
        (project_dir / subdir).mkdir(parents=True)


def run_cmd(command: str):
    status = subprocess.call(shlex.split(command), env=os.environ.copy())
    if status != 0:
        sys.exit(status)


def run_commands(commands: List[str] = tuple(), variables: Dict[str, str] = {}):
    for command in commands:
        # Substitute variables, e.g. "./{NAME}.json"
        command = command.format(**variables)
        msg.info(command)
        run_cmd(command)


@project_cli.command("clone")
def project_clone(
    # fmt: off
    name: str = Arg(..., help="The name of the template to fetch"),
    dest: Path = Arg(Path.cwd(), help="Where to download and work. Defaults to current working directory.", exists=True, file_okay=False),
    repo: str = Opt(about.__projects__, "--repo", "-r", help="The repository to look in."),
    # fmt: on
):
    """Clone a project template from a repository."""
    print("Cloning", repo)


@project_cli.command("run")
def project_run(
    # fmt: off
    project_dir: Path = Arg(..., help="Location of project directory", exists=True, file_okay=False),
    subcommand: str = Arg(None, help="Name of command defined in project config")
    # fmt: on
):
    """Run scripts defined in the project."""
    config = load_project_config(project_dir)
    config_commands = config.get("commands", [])
    variables = config.get("variables", {})
    commands = {cmd["name"]: cmd for cmd in config_commands}
    if subcommand is None:
        all_commands = config.get("run", [])
        if not all_commands:
            msg.warn("No run commands defined in project config", exits=0)
        msg.table([(cmd["name"], cmd.get("help", "")) for cmd in config_commands])
        for command in all_commands:
            if command not in commands:
                msg.fail(f"Can't find command '{command}' in project config", exits=1)
            msg.divider(command)
            run_commands(commands[command]["script"], variables)
        return
    if subcommand not in commands:
        msg.fail(f"Can't find command '{subcommand}' in project config", exits=1)
    run_commands(commands[subcommand]["script"], variables)


app.add_typer(project_cli, name="project")
