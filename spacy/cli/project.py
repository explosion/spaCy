from typing import List, Dict, Any
import typer
import srsly
from pathlib import Path
from wasabi import msg
import subprocess
import shlex
import os
import re

from ._app import app, Arg, Opt
from .. import about
from ..schemas import ProjectConfigSchema, validate
from ..util import ensure_path, run_command


CONFIG_FILE = "project.yml"
DIRS = ["assets", "configs", "packages", "metrics", "scripts", "notebooks", "training"]
CACHES = [
    Path.home() / ".torch",
    Path.home() / ".caches" / "torch",
    os.environ.get("TORCH_HOME"),
    Path.home() / ".keras",
]

project_cli = typer.Typer(help="Command-line interface for spaCy projects")


@project_cli.callback(invoke_without_command=True)
def callback():
    # This runs before every project command and ensures DVC is installed
    try:
        subprocess.run(["dvc", "--version"], stdout=subprocess.DEVNULL)
    except Exception:
        msg.fail(
            "spaCy projects require DVC (Data Version Control) and the 'dvc' command",
            "You can install the Python package from pip (pip install dvc) or "
            "conda (conda install -c conda-forge dvc). For more details, see the "
            "documentation: https://dvc.org/doc/install",
            exits=1,
        )


@project_cli.command("clone")
def project_clone_cli(
    # fmt: off
    name: str = Arg(..., help="The name of the template to fetch"),
    dest: Path = Arg(Path.cwd(), help="Where to download and work. Defaults to current working directory.", exists=True, file_okay=False),
    repo: str = Opt(about.__projects__, "--repo", "-r", help="The repository to look in."),
    # fmt: on
):
    """Clone a project template from a repository."""
    project_clone(name, dest, repo=repo)


def project_clone(name: str, dest: Path, repo: str = about.__projects__) -> None:
    dest = ensure_path(dest)
    if not dest or not dest.exists() or not dest.is_dir():
        msg.fail("Not a valid directory to clone project", dest, exits=1)
    cmd = ["dvc", "get", repo, name, "-o", str(dest)]
    msg.info(" ".join(cmd))
    run_command(cmd)
    msg.good(f"Cloned project '{name}' from {repo}")
    with msg.loading("Setting up directories..."):
        for sub_dir in DIRS:
            dir_path = dest / sub_dir
            if not dir_path.exists():
                dir_path.mkdir(parents=True)
    msg.good(f"Your project is now ready!", dest.resolve())


@project_cli.command("get-assets")
def project_get_assets_cli(
    path: Path = Arg(..., help="Path to cloned project", exists=True, file_okay=False)
):
    """Use Data Version Control to get the assets for the project."""
    project_get_assets(path)


def project_get_assets(project_path: Path) -> None:
    project_path = ensure_path(project_path)
    config = load_project_config(project_path)
    assets = config.get("assets", {})
    if not assets:
        msg.warn(f"No assets specified in {CONFIG_FILE}", exits=0)
    msg.info(f"Getting {len(assets)} asset(s)")
    variables = config.get("variables", {})
    for asset in assets:
        url = asset["url"].format(**variables)
        dest = asset["dest"].format(**variables)
        dest_path = project_path / dest
        check_asset(url)
        cmd = ["dvc", "get-url", url, str(dest_path)]
        msg.info(" ".join(cmd))
        run_command(cmd)
        msg.good(f"Got asset {dest}")


@project_cli.command("run")
def project_run_cli(
    # fmt: off
    project_dir: Path = Arg(..., help="Location of project directory", exists=True, file_okay=False),
    subcommand: str = Arg(None, help="Name of command defined in project config")
    # fmt: on
):
    """Run scripts defined in the project."""
    project_run(project_dir, subcommand)


def project_run(project_dir: Path, subcommand: str) -> None:
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


def load_project_config(path: Path) -> Dict[str, Any]:
    config_path = path / CONFIG_FILE
    if not config_path.exists():
        msg.fail("Can't find project config", config_path, exits=1)
    config = srsly.read_yaml(config_path)
    errors = validate(ProjectConfigSchema, config)
    if errors:
        msg.fail(f"Invalid project config in {CONFIG_FILE}", "\n".join(errors), exits=1)
    return config


def run_commands(commands: List[str] = tuple(), variables: Dict[str, str] = {}) -> None:
    for command in commands:
        # Substitute variables, e.g. "./{NAME}.json"
        command = command.format(**variables)
        msg.info(command)
        run_command(shlex.split(command))


def check_asset(url: str) -> None:
    # If the asset URL is a regular GitHub URL it's likely a mistake
    # TODO: support loading from GitHub URLs? Automatically convert to raw?
    if re.match("(http(s?)):\/\/github.com", url):
        msg.warn(
            "Downloading from a regular GitHub URL. This will only download "
            "the source of the page, not the actual file. If you want to "
            "download the raw file, click on 'Download' on the GitHub page "
            "and copy the raw.githubusercontent.com URL instead."
        )
