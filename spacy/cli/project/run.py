from typing import Optional, List, Dict, Sequence, Any
from pathlib import Path
from wasabi import msg
import typer
import sys
import srsly

from ...util import working_dir, run_command, split_command, is_cwd, get_checksum
from ...util import get_hash, join_command
from .._app import project_cli, Arg, Opt, COMMAND
from .util import PROJECT_FILE, PROJECT_LOCK, load_project_config


@project_cli.command(
    "run", context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def project_run_cli(
    # fmt: off
    ctx: typer.Context,
    subcommand: str = Arg(None, help=f"Name of command defined in the {PROJECT_FILE}"),
    project_dir: Path = Arg(Path.cwd(), help="Location of project directory. Defaults to current working directory.", exists=True, file_okay=False),
    force: bool = Opt(False, "--force", "-F", help="Force re-running steps, even if nothing changed"),
    dry: bool = Opt(False, "--dry", "-D", help="Perform a dry run and don't execute commands"),
    show_help: bool = Opt(False, "--help", help="Show help message and available subcommands")
    # fmt: on
):
    """Run a named script or workflow defined in the project.yml. If a workflow
    name is specified, all commands in the workflow are run, in order. If
    commands define inputs and/or outputs, they will only be re-run if state
    has changed.
    """
    if show_help or not subcommand:
        print_run_help(project_dir, subcommand)
    else:
        project_run(project_dir, subcommand, *ctx.args, force=force, dry=dry)


def project_run(
    project_dir: Path, subcommand: str, *, force: bool = False, dry: bool = False
) -> None:
    """Run a named script defined in the project.yml. If the script is part
    of the default pipeline (defined in the "run" section), DVC is used to
    execute the command, so it can determine whether to rerun it. It then
    calls into "exec" to execute it.

    project_dir (Path): Path to project directory.
    subcommand (str): Name of command to run.
    force (bool): Force re-running, even if nothing changed.
    dry (bool): Perform a dry run and don't execute commands.
    """
    config = load_project_config(project_dir)
    variables = config.get("variables", {})
    commands = {cmd["name"]: cmd for cmd in config.get("commands", [])}
    workflows = config.get("workflows", {})
    validate_subcommand(commands.keys(), workflows.keys(), subcommand)
    if subcommand in workflows:
        msg.info(f"Running workflow '{subcommand}'")
        for cmd in workflows[subcommand]:
            project_run(project_dir, cmd, force=force, dry=dry)
    else:
        cmd = commands[subcommand]
        variables = config.get("variables", {})
        for dep in cmd.get("deps", []):
            dep = dep.format(**variables)
            if not (project_dir / dep).exists():
                err = f"Missing dependency specified by command '{subcommand}': {dep}"
                err_kwargs = {"exits": 1} if not dry else {}
                msg.fail(err, **err_kwargs)
        with working_dir(project_dir) as current_dir:
            rerun = check_rerun(current_dir, cmd, variables)
            if not rerun and not force:
                msg.info(f"Skipping '{cmd['name']}': nothing changed")
            else:
                run_commands(cmd["script"], variables, dry=dry)
                update_lockfile(current_dir, cmd, variables)


def print_run_help(project_dir: Path, subcommand: Optional[str] = None) -> None:
    """Simulate a CLI help prompt using the info available in the project.yml.

    project_dir (Path): The project directory.
    subcommand (Optional[str]): The subcommand or None. If a subcommand is
        provided, the subcommand help is shown. Otherwise, the top-level help
        and a list of available commands is printed.
    """
    config = load_project_config(project_dir)
    config_commands = config.get("commands", [])
    commands = {cmd["name"]: cmd for cmd in config_commands}
    project_loc = "" if is_cwd(project_dir) else project_dir
    if subcommand:
        validate_subcommand(commands.keys(), subcommand)
        print(f"Usage: {COMMAND} project run {subcommand} {project_loc}")
        help_text = commands[subcommand].get("help")
        if help_text:
            msg.text(f"\n{help_text}\n")
    else:
        print(f"\nAvailable commands in {PROJECT_FILE}")
        print(f"Usage: {COMMAND} project run [COMMAND] {project_loc}")
        msg.table([(cmd["name"], cmd.get("help", "")) for cmd in config_commands])
        msg.text(f"Run all commands defined in the 'run' block of the {PROJECT_FILE}:")
        print(f"{COMMAND} project run {project_loc}")


def run_commands(
    commands: List[str] = tuple(),
    variables: Dict[str, str] = {},
    silent: bool = False,
    dry: bool = False,
) -> None:
    """Run a sequence of commands in a subprocess, in order.

    commands (List[str]): The string commands.
    variables (Dict[str, str]): Dictionary of variable names, mapped to their
        values. Will be used to substitute format string variables in the
        commands.
    silent (bool): Don't print the commands.
    dry (bool): Perform a dry run and don't execut anything.
    """
    for command in commands:
        # Substitute variables, e.g. "./{NAME}.json"
        command = command.format(**variables)
        command = split_command(command)
        # Not sure if this is needed or a good idea. Motivation: users may often
        # use commands in their config that reference "python" and we want to
        # make sure that it's always executing the same Python that spaCy is
        # executed with and the pip in the same env, not some other Python/pip.
        # Also ensures cross-compatibility if user 1 writes "python3" (because
        # that's how it's set up on their system), and user 2 without the
        # shortcut tries to re-run the command.
        if len(command) and command[0] in ("python", "python3"):
            command[0] = sys.executable
        elif len(command) and command[0] in ("pip", "pip3"):
            command = [sys.executable, "-m", "pip", *command[1:]]
        if not silent:
            print(f"Running command: {join_command(command)}")
        if not dry:
            run_command(command)


def validate_subcommand(
    commands: Sequence[str], workflows: Sequence[str], subcommand: str
) -> None:
    """Check that a subcommand is valid and defined. Raises an error otherwise.

    commands (Sequence[str]): The available commands.
    subcommand (str): The subcommand.
    """
    if not commands and not workflows:
        msg.fail(f"No commands or workflows defined in {PROJECT_FILE}", exits=1)
    if subcommand not in commands and subcommand not in workflows:
        help_msg = []
        if commands:
            help_msg.append(f"Available commands: {', '.join(commands)}")
        if workflows:
            help_msg.append(f"Available workflows: {', '.join(workflows)}")
        msg.fail(
            f"Can't find command or workflow '{subcommand}' in {PROJECT_FILE}",
            ". ".join(help_msg),
            exits=1,
        )


def check_rerun(
    project_dir: Path, command: Dict[str, Any], variables: Dict[str, str] = {}
):
    lock_path = project_dir / PROJECT_LOCK
    if not lock_path.exists():  # We don't have a lockfile, run command
        return True
    data = srsly.read_yaml(lock_path)
    if command["name"] not in data:  # We don't have info about this command
        return True
    entry = data[command["name"]]
    # If the entry in the lockfile matches the lockfile entry that would be
    # generated from the current command, we don't rerun
    return get_hash(get_lock_entry(project_dir, command, variables)) != get_hash(entry)


def update_lockfile(
    project_dir: Path, command: Dict[str, Any], variables: Dict[str, str] = {}
):
    lock_path = project_dir / PROJECT_LOCK
    if not lock_path.exists():
        srsly.write_yaml(lock_path, {})
        data = {}
    else:
        data = srsly.read_yaml(lock_path)
    data[command["name"]] = get_lock_entry(project_dir, command, variables)
    srsly.write_yaml(lock_path, data)


def get_lock_entry(project_dir, command, variables):
    deps = get_fileinfo(project_dir, command.get("deps", []), variables)
    outs = get_fileinfo(project_dir, command.get("outputs", []), variables)
    outs_nc = get_fileinfo(project_dir, command.get("outputs_no_cache", []), variables)
    return {
        "cmd": f"{COMMAND} run {command['name']}",
        "script": command["script"],
        "deps": deps,
        "outs": [*outs, *outs_nc],
    }


def get_fileinfo(project_dir: Path, paths: List[str], variables: Dict[str, str] = {}):
    data = []
    for path in paths:
        path = path.format(**variables)
        file_path = project_dir / path
        md5 = get_checksum(file_path) if file_path.exists() else None
        data.append({"path": path, "md5": md5})
    return data
