from typing import Optional, List, Dict, Sequence, Any, Iterable, Tuple
import os.path
from pathlib import Path

from wasabi import msg
from wasabi.util import locale_escape
import sys
import srsly
import typer

from ... import about
from ...git_info import GIT_VERSION
from ...util import working_dir, run_command, split_command, is_cwd, join_command
from ...util import SimpleFrozenList, is_minor_version_match, ENV_VARS
from ...util import check_bool_env_var, SimpleFrozenDict
from .._util import PROJECT_FILE, PROJECT_LOCK, load_project_config, get_hash
from .._util import get_checksum, project_cli, Arg, Opt, COMMAND, parse_config_overrides


@project_cli.command(
    "run", context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def project_run_cli(
    # fmt: off
    ctx: typer.Context,  # This is only used to read additional arguments
    subcommand: str = Arg(None, help=f"Name of command defined in the {PROJECT_FILE}"),
    project_dir: Path = Arg(Path.cwd(), help="Location of project directory. Defaults to current working directory.", exists=True, file_okay=False),
    force: bool = Opt(False, "--force", "-F", help="Force re-running steps, even if nothing changed"),
    dry: bool = Opt(False, "--dry", "-D", help="Perform a dry run and don't execute scripts"),
    show_help: bool = Opt(False, "--help", help="Show help message and available subcommands")
    # fmt: on
):
    """Run a named command or workflow defined in the project.yml. If a workflow
    name is specified, all commands in the workflow are run, in order. If
    commands define dependencies and/or outputs, they will only be re-run if
    state has changed.

    DOCS: https://spacy.io/api/cli#project-run
    """
    if show_help or not subcommand:
        print_run_help(project_dir, subcommand)
    else:
        overrides = parse_config_overrides(ctx.args)
        project_run(project_dir, subcommand, overrides=overrides, force=force, dry=dry)


def project_run(
    project_dir: Path,
    subcommand: str,
    *,
    overrides: Dict[str, Any] = SimpleFrozenDict(),
    force: bool = False,
    dry: bool = False,
    capture: bool = False,
    skip_requirements_check: bool = False,
) -> None:
    """Run a named script defined in the project.yml. If the script is part
    of the default pipeline (defined in the "run" section), DVC is used to
    execute the command, so it can determine whether to rerun it. It then
    calls into "exec" to execute it.

    project_dir (Path): Path to project directory.
    subcommand (str): Name of command to run.
    overrides (Dict[str, Any]): Optional config overrides.
    force (bool): Force re-running, even if nothing changed.
    dry (bool): Perform a dry run and don't execute commands.
    capture (bool): Whether to capture the output and errors of individual commands.
        If False, the stdout and stderr will not be redirected, and if there's an error,
        sys.exit will be called with the return code. You should use capture=False
        when you want to turn over execution to the command, and capture=True
        when you want to run the command more like a function.
    skip_requirements_check (bool): Whether to skip the requirements check.
    """
    config = load_project_config(project_dir, overrides=overrides)
    commands = {cmd["name"]: cmd for cmd in config.get("commands", [])}
    workflows = config.get("workflows", {})
    validate_subcommand(list(commands.keys()), list(workflows.keys()), subcommand)

    req_path = project_dir / "requirements.txt"
    if not skip_requirements_check:
        if config.get("check_requirements", True) and os.path.exists(req_path):
            with req_path.open() as requirements_file:
                _check_requirements([req.strip() for req in requirements_file])

    if subcommand in workflows:
        msg.info(f"Running workflow '{subcommand}'")
        for cmd in workflows[subcommand]:
            project_run(
                project_dir,
                cmd,
                overrides=overrides,
                force=force,
                dry=dry,
                capture=capture,
                skip_requirements_check=True,
            )
    else:
        cmd = commands[subcommand]
        for dep in cmd.get("deps", []):
            if not (project_dir / dep).exists():
                err = f"Missing dependency specified by command '{subcommand}': {dep}"
                err_help = "Maybe you forgot to run the 'project assets' command or a previous step?"
                err_exits = 1 if not dry else None
                msg.fail(err, err_help, exits=err_exits)
        check_spacy_commit = check_bool_env_var(ENV_VARS.PROJECT_USE_GIT_VERSION)
        with working_dir(project_dir) as current_dir:
            msg.divider(subcommand)
            rerun = check_rerun(current_dir, cmd, check_spacy_commit=check_spacy_commit)
            if not rerun and not force:
                msg.info(f"Skipping '{cmd['name']}': nothing changed")
            else:
                run_commands(cmd["script"], dry=dry, capture=capture)
                if not dry:
                    update_lockfile(current_dir, cmd)


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
    workflows = config.get("workflows", {})
    project_loc = "" if is_cwd(project_dir) else project_dir
    if subcommand:
        validate_subcommand(list(commands.keys()), list(workflows.keys()), subcommand)
        print(f"Usage: {COMMAND} project run {subcommand} {project_loc}")
        if subcommand in commands:
            help_text = commands[subcommand].get("help")
            if help_text:
                print(f"\n{help_text}\n")
        elif subcommand in workflows:
            steps = workflows[subcommand]
            print(f"\nWorkflow consisting of {len(steps)} commands:")
            steps_data = [
                (f"{i + 1}. {step}", commands[step].get("help", ""))
                for i, step in enumerate(steps)
            ]
            msg.table(steps_data)
            help_cmd = f"{COMMAND} project run [COMMAND] {project_loc} --help"
            print(f"For command details, run: {help_cmd}")
    else:
        print("")
        title = config.get("title")
        if title:
            print(f"{locale_escape(title)}\n")
        if config_commands:
            print(f"Available commands in {PROJECT_FILE}")
            print(f"Usage: {COMMAND} project run [COMMAND] {project_loc}")
            msg.table([(cmd["name"], cmd.get("help", "")) for cmd in config_commands])
        if workflows:
            print(f"Available workflows in {PROJECT_FILE}")
            print(f"Usage: {COMMAND} project run [WORKFLOW] {project_loc}")
            msg.table([(name, " -> ".join(steps)) for name, steps in workflows.items()])


def run_commands(
    commands: Iterable[str] = SimpleFrozenList(),
    silent: bool = False,
    dry: bool = False,
    capture: bool = False,
) -> None:
    """Run a sequence of commands in a subprocess, in order.

    commands (List[str]): The string commands.
    silent (bool): Don't print the commands.
    dry (bool): Perform a dry run and don't execut anything.
    capture (bool): Whether to capture the output and errors of individual commands.
        If False, the stdout and stderr will not be redirected, and if there's an error,
        sys.exit will be called with the return code. You should use capture=False
        when you want to turn over execution to the command, and capture=True
        when you want to run the command more like a function.
    """
    for c in commands:
        command = split_command(c)
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
            run_command(command, capture=capture)


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
        if subcommand in ["assets", "asset"]:
            help_msg.append("Did you mean to run: python -m spacy project assets?")
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
    project_dir: Path,
    command: Dict[str, Any],
    *,
    check_spacy_version: bool = True,
    check_spacy_commit: bool = False,
) -> bool:
    """Check if a command should be rerun because its settings or inputs/outputs
    changed.

    project_dir (Path): The current project directory.
    command (Dict[str, Any]): The command, as defined in the project.yml.
    strict_version (bool):
    RETURNS (bool): Whether to re-run the command.
    """
    # Always rerun if no-skip is set
    if command.get("no_skip", False):
        return True
    lock_path = project_dir / PROJECT_LOCK
    if not lock_path.exists():  # We don't have a lockfile, run command
        return True
    data = srsly.read_yaml(lock_path)
    if command["name"] not in data:  # We don't have info about this command
        return True
    entry = data[command["name"]]
    # Always run commands with no outputs (otherwise they'd always be skipped)
    if not entry.get("outs", []):
        return True
    # Always rerun if spaCy version or commit hash changed
    spacy_v = entry.get("spacy_version")
    commit = entry.get("spacy_git_version")
    if check_spacy_version and not is_minor_version_match(spacy_v, about.__version__):
        info = f"({spacy_v} in {PROJECT_LOCK}, {about.__version__} current)"
        msg.info(f"Re-running '{command['name']}': spaCy minor version changed {info}")
        return True
    if check_spacy_commit and commit != GIT_VERSION:
        info = f"({commit} in {PROJECT_LOCK}, {GIT_VERSION} current)"
        msg.info(f"Re-running '{command['name']}': spaCy commit changed {info}")
        return True
    # If the entry in the lockfile matches the lockfile entry that would be
    # generated from the current command, we don't rerun because it means that
    # all inputs/outputs, hashes and scripts are the same and nothing changed
    lock_entry = get_lock_entry(project_dir, command)
    exclude = ["spacy_version", "spacy_git_version"]
    return get_hash(lock_entry, exclude=exclude) != get_hash(entry, exclude=exclude)


def update_lockfile(project_dir: Path, command: Dict[str, Any]) -> None:
    """Update the lockfile after running a command. Will create a lockfile if
    it doesn't yet exist and will add an entry for the current command, its
    script and dependencies/outputs.

    project_dir (Path): The current project directory.
    command (Dict[str, Any]): The command, as defined in the project.yml.
    """
    lock_path = project_dir / PROJECT_LOCK
    if not lock_path.exists():
        srsly.write_yaml(lock_path, {})
        data = {}
    else:
        data = srsly.read_yaml(lock_path)
    data[command["name"]] = get_lock_entry(project_dir, command)
    srsly.write_yaml(lock_path, data)


def get_lock_entry(project_dir: Path, command: Dict[str, Any]) -> Dict[str, Any]:
    """Get a lockfile entry for a given command. An entry includes the command,
    the script (command steps) and a list of dependencies and outputs with
    their paths and file hashes, if available. The format is based on the
    dvc.lock files, to keep things consistent.

    project_dir (Path): The current project directory.
    command (Dict[str, Any]): The command, as defined in the project.yml.
    RETURNS (Dict[str, Any]): The lockfile entry.
    """
    deps = get_fileinfo(project_dir, command.get("deps", []))
    outs = get_fileinfo(project_dir, command.get("outputs", []))
    outs_nc = get_fileinfo(project_dir, command.get("outputs_no_cache", []))
    return {
        "cmd": f"{COMMAND} run {command['name']}",
        "script": command["script"],
        "deps": deps,
        "outs": [*outs, *outs_nc],
        "spacy_version": about.__version__,
        "spacy_git_version": GIT_VERSION,
    }


def get_fileinfo(project_dir: Path, paths: List[str]) -> List[Dict[str, Optional[str]]]:
    """Generate the file information for a list of paths (dependencies, outputs).
    Includes the file path and the file's checksum.

    project_dir (Path): The current project directory.
    paths (List[str]): The file paths.
    RETURNS (List[Dict[str, str]]): The lockfile entry for a file.
    """
    data = []
    for path in paths:
        file_path = project_dir / path
        md5 = get_checksum(file_path) if file_path.exists() else None
        data.append({"path": path, "md5": md5})
    return data


def _check_requirements(requirements: List[str]) -> Tuple[bool, bool]:
    """Checks whether requirements are installed and free of version conflicts.
    requirements (List[str]): List of requirements.
    RETURNS (Tuple[bool, bool]): Whether (1) any packages couldn't be imported, (2) any packages with version conflicts
        exist.
    """
    import pkg_resources

    failed_pkgs_msgs: List[str] = []
    conflicting_pkgs_msgs: List[str] = []

    for req in requirements:
        try:
            pkg_resources.require(req)
        except pkg_resources.DistributionNotFound as dnf:
            failed_pkgs_msgs.append(dnf.report())
        except pkg_resources.VersionConflict as vc:
            conflicting_pkgs_msgs.append(vc.report())
        except Exception:
            msg.warn(
                f"Unable to check requirement: {req} "
                "Checks are currently limited to requirement specifiers "
                "(PEP 508)"
            )

    if len(failed_pkgs_msgs) or len(conflicting_pkgs_msgs):
        msg.warn(
            title="Missing requirements or requirement conflicts detected. Make sure your Python environment is set up "
            "correctly and you installed all requirements specified in your project's requirements.txt: "
        )
        for pgk_msg in failed_pkgs_msgs + conflicting_pkgs_msgs:
            msg.text(pgk_msg)

    return len(failed_pkgs_msgs) > 0, len(conflicting_pkgs_msgs) > 0
