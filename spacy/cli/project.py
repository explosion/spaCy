from typing import List, Dict, Any
import typer
import srsly
from pathlib import Path
from wasabi import msg
import subprocess
import shlex
import os
import re
import shutil
import sys

from ._app import app, Arg, Opt, COMMAND
from .. import about
from ..schemas import ProjectConfigSchema, validate
from ..util import ensure_path, run_command, make_tempdir, working_dir


CONFIG_FILE = "project.yml"
DIRS = [
    "assets",
    "metas",
    "configs",
    "packages",
    "metrics",
    "scripts",
    "notebooks",
    "training",
    "corpus",
]
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
    dest: Path = Arg(Path.cwd(), help="Where to download and work. Defaults to current working directory.", exists=False),
    repo: str = Opt(about.__projects__, "--repo", "-r", help="The repository to look in."),
    verbose: bool = Opt(False, "--verbose", "-V", help="Show detailed information")
    # fmt: on
):
    """Clone a project template from a repository."""
    project_clone(name, dest, repo=repo, verbose=verbose)


def project_clone(
    name: str, dest: Path, *, repo: str = about.__projects__, verbose: bool = False
) -> None:
    dest = ensure_path(dest)
    check_clone_dest(dest)
    # When cloning a subdirectory with DVC, it will create a folder of that name
    # within the destination dir, so we use a tempdir and then copy it into the
    # parent directory to create the cloned directory
    with make_tempdir() as tmp_dir:
        cmd = ["dvc", "get", repo, name, "-o", str(tmp_dir)]
        if verbose:
            cmd.append("-v")
        print(" ".join(cmd))
        run_command(cmd)
        shutil.move(str(tmp_dir / Path(name).name), str(dest))
    msg.good(f"Cloned project '{name}' from {repo}")
    for sub_dir in DIRS:
        dir_path = dest / sub_dir
        if not dir_path.exists():
            dir_path.mkdir(parents=True)
    msg.good(f"Your project is now ready!", dest.resolve())
    print(f"To get the assets, run:\npython -m spacy project get-assets {dest}")


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
        run_command(cmd)
        msg.good(f"Got asset {dest}")


@project_cli.command("run")
def project_run_cli(
    # fmt: off
    project_dir: Path = Arg(..., help="Location of project directory", exists=True, file_okay=False),
    subcommand: str = Arg(None, help="Name of command defined in project config"),
    show_help: bool = Opt(False, "--help", help="Show help message and available subcommands")
    # fmt: on
):
    """Run scripts defined in the project."""
    if show_help:
        print_run_help(project_dir, subcommand)
    else:
        project_run(project_dir, subcommand)


def print_run_help(project_dir: Path, subcommand: str) -> None:
    """Simulate a CLI help prompt using the info available in the project config."""
    config = load_project_config(project_dir)
    config_commands = config.get("commands", [])
    commands = {cmd["name"]: cmd for cmd in config_commands}
    if subcommand:
        if subcommand not in commands:
            msg.fail(f"Can't find command '{subcommand}' in project config", exits=1)
        print(f"Usage: {COMMAND} project run {project_dir} {subcommand}")
        help_text = commands[subcommand].get("help")
        if help_text:
            msg.text(f"\n{help_text}\n")
    else:
        print(f"\nAvailable commands in {CONFIG_FILE}")
        print(f"Usage: {COMMAND} project run {project_dir} [COMMAND]")
        msg.table([(cmd["name"], cmd.get("help", "")) for cmd in config_commands])


def project_run(project_dir: Path, subcommand: str) -> None:
    config = load_project_config(project_dir)
    config_commands = config.get("commands", [])
    variables = config.get("variables", {})
    commands = {cmd["name"]: cmd for cmd in config_commands}
    if subcommand and subcommand not in commands:
        msg.fail(f"Can't find command '{subcommand}' in project config", exits=1)
    with working_dir(project_dir):
        if subcommand is None:
            all_commands = config.get("run", [])
            if not all_commands:
                msg.warn("No run commands defined in project config", exits=0)
            msg.table([(cmd["name"], cmd.get("help", "")) for cmd in config_commands])
            for command in all_commands:
                if command not in commands:
                    msg.fail(
                        f"Can't find command '{command}' in project config", exits=1
                    )
                msg.divider(command)
                run_commands(commands[command]["script"], variables)
        else:
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
        command = shlex.split(command)
        # TODO: is this needed / a good idea?
        if len(command) and command[0] == "python":
            command[0] = sys.executable
        print(" ".join(command))
        run_command(command)


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
        # url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/").replace("/tree/", "/")


def check_clone_dest(dest: Path) -> None:
    """Check and validate that the destination path can be used to clone."""
    if not dest:
        msg.fail(f"Not a valid directory to clone project: {dest}", exits=1)
    if dest.exists():
        # Directory already exists (not allowed, clone needs to create it)
        msg.fail(f"Can't clone project, directory already exists: {dest}", exits=1)
    if not dest.parent.exists():
        # We're not creating parents, parent dir should exist
        msg.fail(
            f"Can't clone project, parent directory doesn't exist: {dest.parent}",
            exits=1,
        )
