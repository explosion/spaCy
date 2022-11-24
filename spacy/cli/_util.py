from typing import Dict, Any, Union, List, Optional, Tuple, Iterable
from typing import TYPE_CHECKING, overload
import sys
import shutil
from pathlib import Path
from wasabi import msg, Printer
import srsly
import hashlib
import typer
from click import NoSuchOption
from click.parser import split_arg_string
from typer.main import get_command
from contextlib import contextmanager
from thinc.api import Config, ConfigValidationError, require_gpu
from thinc.util import gpu_is_available
from configparser import InterpolationError
import os

from ..compat import Literal
from ..schemas import ProjectConfigSchema, validate
from ..util import import_file, run_command, make_tempdir, registry, logger
from ..util import is_compatible_version, SimpleFrozenDict, ENV_VARS
from .. import about

if TYPE_CHECKING:
    from pathy import Pathy  # noqa: F401


SDIST_SUFFIX = ".tar.gz"
WHEEL_SUFFIX = "-py3-none-any.whl"

PROJECT_FILE = "project.yml"
PROJECT_LOCK = "project.lock"
COMMAND = "python -m spacy"
NAME = "spacy"
HELP = """spaCy Command-line Interface

DOCS: https://spacy.io/api/cli
"""
PROJECT_HELP = f"""Command-line interface for spaCy projects and templates.
You'd typically start by cloning a project template to a local directory and
fetching its assets like datasets etc. See the project's {PROJECT_FILE} for the
available commands.
"""
DEBUG_HELP = """Suite of helpful commands for debugging and profiling. Includes
commands to check and validate your config files, training and evaluation data,
and custom model implementations.
"""
INIT_HELP = """Commands for initializing configs and pipeline packages."""

# Wrappers for Typer's annotations. Initially created to set defaults and to
# keep the names short, but not needed at the moment.
Arg = typer.Argument
Opt = typer.Option

app = typer.Typer(name=NAME, help=HELP)
project_cli = typer.Typer(name="project", help=PROJECT_HELP, no_args_is_help=True)
debug_cli = typer.Typer(name="debug", help=DEBUG_HELP, no_args_is_help=True)
init_cli = typer.Typer(name="init", help=INIT_HELP, no_args_is_help=True)

app.add_typer(project_cli)
app.add_typer(debug_cli)
app.add_typer(init_cli)


def setup_cli() -> None:
    # Make sure the entry-point for CLI runs, so that they get imported.
    registry.cli.get_all()
    # Ensure that the help messages always display the correct prompt
    command = get_command(app)
    command(prog_name=COMMAND)


def parse_config_overrides(
    args: List[str], env_var: Optional[str] = ENV_VARS.CONFIG_OVERRIDES
) -> Dict[str, Any]:
    """Generate a dictionary of config overrides based on the extra arguments
    provided on the CLI, e.g. --training.batch_size to override
    "training.batch_size". Arguments without a "." are considered invalid,
    since the config only allows top-level sections to exist.

    env_vars (Optional[str]): Optional environment variable to read from.
    RETURNS (Dict[str, Any]): The parsed dict, keyed by nested config setting.
    """
    env_string = os.environ.get(env_var, "") if env_var else ""
    env_overrides = _parse_overrides(split_arg_string(env_string))
    cli_overrides = _parse_overrides(args, is_cli=True)
    if cli_overrides:
        keys = [k for k in cli_overrides if k not in env_overrides]
        logger.debug(f"Config overrides from CLI: {keys}")
    if env_overrides:
        logger.debug(f"Config overrides from env variables: {list(env_overrides)}")
    return {**cli_overrides, **env_overrides}


def _parse_overrides(args: List[str], is_cli: bool = False) -> Dict[str, Any]:
    result = {}
    while args:
        opt = args.pop(0)
        err = f"Invalid config override '{opt}'"
        if opt.startswith("--"):  # new argument
            orig_opt = opt
            opt = opt.replace("--", "")
            if "." not in opt:
                if is_cli:
                    raise NoSuchOption(orig_opt)
                else:
                    msg.fail(f"{err}: can't override top-level sections", exits=1)
            if "=" in opt:  # we have --opt=value
                opt, value = opt.split("=", 1)
                opt = opt.replace("-", "_")
            else:
                if not args or args[0].startswith("--"):  # flag with no value
                    value = "true"
                else:
                    value = args.pop(0)
            result[opt] = _parse_override(value)
        else:
            msg.fail(f"{err}: name should start with --", exits=1)
    return result


def _parse_override(value: Any) -> Any:
    # Just like we do in the config, we're calling json.loads on the
    # values. But since they come from the CLI, it'd be unintuitive to
    # explicitly mark strings with escaped quotes. So we're working
    # around that here by falling back to a string if parsing fails.
    # TODO: improve logic to handle simple types like list of strings?
    try:
        return srsly.json_loads(value)
    except ValueError:
        return str(value)


def load_project_config(
    path: Path, interpolate: bool = True, overrides: Dict[str, Any] = SimpleFrozenDict()
) -> Dict[str, Any]:
    """Load the project.yml file from a directory and validate it. Also make
    sure that all directories defined in the config exist.

    path (Path): The path to the project directory.
    interpolate (bool): Whether to substitute project variables.
    overrides (Dict[str, Any]): Optional config overrides.
    RETURNS (Dict[str, Any]): The loaded project.yml.
    """
    config_path = path / PROJECT_FILE
    if not config_path.exists():
        msg.fail(f"Can't find {PROJECT_FILE}", config_path, exits=1)
    invalid_err = f"Invalid {PROJECT_FILE}. Double-check that the YAML is correct."
    try:
        config = srsly.read_yaml(config_path)
    except ValueError as e:
        msg.fail(invalid_err, e, exits=1)
    errors = validate(ProjectConfigSchema, config)
    if errors:
        msg.fail(invalid_err)
        print("\n".join(errors))
        sys.exit(1)
    validate_project_version(config)
    validate_project_commands(config)
    # Make sure directories defined in config exist
    for subdir in config.get("directories", []):
        dir_path = path / subdir
        if not dir_path.exists():
            dir_path.mkdir(parents=True)
    if interpolate:
        err = f"{PROJECT_FILE} validation error"
        with show_validation_error(title=err, hint_fill=False):
            config = substitute_project_variables(config, overrides)
    return config


def substitute_project_variables(
    config: Dict[str, Any],
    overrides: Dict[str, Any] = SimpleFrozenDict(),
    key: str = "vars",
    env_key: str = "env",
) -> Dict[str, Any]:
    """Interpolate variables in the project file using the config system.

    config (Dict[str, Any]): The project config.
    overrides (Dict[str, Any]): Optional config overrides.
    key (str): Key containing variables in project config.
    env_key (str): Key containing environment variable mapping in project config.
    RETURNS (Dict[str, Any]): The interpolated project config.
    """
    config.setdefault(key, {})
    config.setdefault(env_key, {})
    # Substitute references to env vars with their values
    for config_var, env_var in config[env_key].items():
        config[env_key][config_var] = _parse_override(os.environ.get(env_var, ""))
    # Need to put variables in the top scope again so we can have a top-level
    # section "project" (otherwise, a list of commands in the top scope wouldn't)
    # be allowed by Thinc's config system
    cfg = Config({"project": config, key: config[key], env_key: config[env_key]})
    cfg = Config().from_str(cfg.to_str(), overrides=overrides)
    interpolated = cfg.interpolate()
    return dict(interpolated["project"])


def validate_project_version(config: Dict[str, Any]) -> None:
    """If the project defines a compatible spaCy version range, chec that it's
    compatible with the current version of spaCy.

    config (Dict[str, Any]): The loaded config.
    """
    spacy_version = config.get("spacy_version", None)
    if spacy_version and not is_compatible_version(about.__version__, spacy_version):
        err = (
            f"The {PROJECT_FILE} specifies a spaCy version range ({spacy_version}) "
            f"that's not compatible with the version of spaCy you're running "
            f"({about.__version__}). You can edit version requirement in the "
            f"{PROJECT_FILE} to load it, but the project may not run as expected."
        )
        msg.fail(err, exits=1)


def validate_project_commands(config: Dict[str, Any]) -> None:
    """Check that project commands and workflows are valid, don't contain
    duplicates, don't clash  and only refer to commands that exist.

    config (Dict[str, Any]): The loaded config.
    """
    command_names = [cmd["name"] for cmd in config.get("commands", [])]
    workflows = config.get("workflows", {})
    duplicates = set([cmd for cmd in command_names if command_names.count(cmd) > 1])
    if duplicates:
        err = f"Duplicate commands defined in {PROJECT_FILE}: {', '.join(duplicates)}"
        msg.fail(err, exits=1)
    for workflow_name, workflow_steps in workflows.items():
        if workflow_name in command_names:
            err = f"Can't use workflow name '{workflow_name}': name already exists as a command"
            msg.fail(err, exits=1)
        for step in workflow_steps:
            if step not in command_names:
                msg.fail(
                    f"Unknown command specified in workflow '{workflow_name}': {step}",
                    f"Workflows can only refer to commands defined in the 'commands' "
                    f"section of the {PROJECT_FILE}.",
                    exits=1,
                )


def get_hash(data, exclude: Iterable[str] = tuple()) -> str:
    """Get the hash for a JSON-serializable object.

    data: The data to hash.
    exclude (Iterable[str]): Top-level keys to exclude if data is a dict.
    RETURNS (str): The hash.
    """
    if isinstance(data, dict):
        data = {k: v for k, v in data.items() if k not in exclude}
    data_str = srsly.json_dumps(data, sort_keys=True).encode("utf8")
    return hashlib.md5(data_str).hexdigest()


def get_checksum(path: Union[Path, str]) -> str:
    """Get the checksum for a file or directory given its file path. If a
    directory path is provided, this uses all files in that directory.

    path (Union[Path, str]): The file or directory path.
    RETURNS (str): The checksum.
    """
    path = Path(path)
    if not (path.is_file() or path.is_dir()):
        msg.fail(f"Can't get checksum for {path}: not a file or directory", exits=1)
    if path.is_file():
        return hashlib.md5(Path(path).read_bytes()).hexdigest()
    else:
        # TODO: this is currently pretty slow
        dir_checksum = hashlib.md5()
        for sub_file in sorted(fp for fp in path.rglob("*") if fp.is_file()):
            dir_checksum.update(sub_file.read_bytes())
        return dir_checksum.hexdigest()


@contextmanager
def show_validation_error(
    file_path: Optional[Union[str, Path]] = None,
    *,
    title: Optional[str] = None,
    desc: str = "",
    show_config: Optional[bool] = None,
    hint_fill: bool = True,
):
    """Helper to show custom config validation errors on the CLI.

    file_path (str / Path): Optional file path of config file, used in hints.
    title (str): Override title of custom formatted error.
    desc (str): Override description of custom formatted error.
    show_config (bool): Whether to output the config the error refers to.
    hint_fill (bool): Show hint about filling config.
    """
    try:
        yield
    except ConfigValidationError as e:
        title = title if title is not None else e.title
        if e.desc:
            desc = f"{e.desc}" if not desc else f"{e.desc}\n\n{desc}"
        # Re-generate a new error object with overrides
        err = e.from_error(e, title="", desc=desc, show_config=show_config)
        msg.fail(title)
        print(err.text.strip())
        if hint_fill and "value_error.missing" in err.error_types:
            config_path = (
                file_path
                if file_path is not None and str(file_path) != "-"
                else "config.cfg"
            )
            msg.text(
                "If your config contains missing values, you can run the 'init "
                "fill-config' command to fill in all the defaults, if possible:",
                spaced=True,
            )
            print(f"{COMMAND} init fill-config {config_path} {config_path} \n")
        sys.exit(1)
    except InterpolationError as e:
        msg.fail("Config validation error", e, exits=1)


def import_code(code_path: Optional[Union[Path, str]]) -> None:
    """Helper to import Python file provided in training commands / commands
    using the config. This makes custom registered functions available.
    """
    if code_path is not None:
        if not Path(code_path).exists():
            msg.fail("Path to Python code not found", code_path, exits=1)
        try:
            import_file("python_code", code_path)
        except Exception as e:
            msg.fail(f"Couldn't load Python code: {code_path}", e, exits=1)


def upload_file(src: Path, dest: Union[str, "Pathy"]) -> None:
    """Upload a file.

    src (Path): The source path.
    url (str): The destination URL to upload to.
    """
    import smart_open

    dest = str(dest)
    with smart_open.open(dest, mode="wb") as output_file:
        with src.open(mode="rb") as input_file:
            output_file.write(input_file.read())


def download_file(src: Union[str, "Pathy"], dest: Path, *, force: bool = False) -> None:
    """Download a file using smart_open.

    url (str): The URL of the file.
    dest (Path): The destination path.
    force (bool): Whether to force download even if file exists.
        If False, the download will be skipped.
    """
    import smart_open

    if dest.exists() and not force:
        return None
    src = str(src)
    with smart_open.open(src, mode="rb", compression="disable") as input_file:
        with dest.open(mode="wb") as output_file:
            shutil.copyfileobj(input_file, output_file)


def ensure_pathy(path):
    """Temporary helper to prevent importing Pathy globally (which can cause
    slow and annoying Google Cloud warning)."""
    from pathy import Pathy  # noqa: F811

    return Pathy(path)


def git_checkout(
    repo: str, subpath: str, dest: Path, *, branch: str = "master", sparse: bool = False
):
    git_version = get_git_version()
    if dest.exists():
        msg.fail("Destination of checkout must not exist", exits=1)
    if not dest.parent.exists():
        msg.fail("Parent of destination of checkout must exist", exits=1)
    if sparse and git_version >= (2, 22):
        return git_sparse_checkout(repo, subpath, dest, branch)
    elif sparse:
        # Only show warnings if the user explicitly wants sparse checkout but
        # the Git version doesn't support it
        err_old = (
            f"You're running an old version of Git (v{git_version[0]}.{git_version[1]}) "
            f"that doesn't fully support sparse checkout yet."
        )
        err_unk = "You're running an unknown version of Git, so sparse checkout has been disabled."
        msg.warn(
            f"{err_unk if git_version == (0, 0) else err_old} "
            f"This means that more files than necessary may be downloaded "
            f"temporarily. To only download the files needed, make sure "
            f"you're using Git v2.22 or above."
        )
    with make_tempdir() as tmp_dir:
        cmd = f"git -C {tmp_dir} clone {repo} . -b {branch}"
        run_command(cmd, capture=True)
        # We need Path(name) to make sure we also support subdirectories
        try:
            source_path = tmp_dir / Path(subpath)
            if not is_subpath_of(tmp_dir, source_path):
                err = f"'{subpath}' is a path outside of the cloned repository."
                msg.fail(err, repo, exits=1)
            shutil.copytree(str(source_path), str(dest))
        except FileNotFoundError:
            err = f"Can't clone {subpath}. Make sure the directory exists in the repo (branch '{branch}')"
            msg.fail(err, repo, exits=1)


def git_sparse_checkout(repo, subpath, dest, branch):
    # We're using Git, partial clone and sparse checkout to
    # only clone the files we need
    # This ends up being RIDICULOUS. omg.
    # So, every tutorial and SO post talks about 'sparse checkout'...But they
    # go and *clone* the whole repo. Worthless. And cloning part of a repo
    # turns out to be completely broken. The only way to specify a "path" is..
    # a path *on the server*? The contents of which, specifies the paths. Wat.
    # Obviously this is hopelessly broken and insecure, because you can query
    # arbitrary paths on the server! So nobody enables this.
    # What we have to do is disable *all* files. We could then just checkout
    # the path, and it'd "work", but be hopelessly slow...Because it goes and
    # transfers every missing object one-by-one. So the final piece is that we
    # need to use some weird git internals to fetch the missings in bulk, and
    # *that* we can do by path.
    # We're using Git and sparse checkout to only clone the files we need
    with make_tempdir() as tmp_dir:
        # This is the "clone, but don't download anything" part.
        cmd = (
            f"git clone {repo} {tmp_dir} --no-checkout --depth 1 "
            f"-b {branch} --filter=blob:none"
        )
        run_command(cmd)
        # Now we need to find the missing filenames for the subpath we want.
        # Looking for this 'rev-list' command in the git --help? Hah.
        cmd = f"git -C {tmp_dir} rev-list --objects --all --missing=print -- {subpath}"
        ret = run_command(cmd, capture=True)
        git_repo = _http_to_git(repo)
        # Now pass those missings into another bit of git internals
        missings = " ".join([x[1:] for x in ret.stdout.split() if x.startswith("?")])
        if not missings:
            err = (
                f"Could not find any relevant files for '{subpath}'. "
                f"Did you specify a correct and complete path within repo '{repo}' "
                f"and branch {branch}?"
            )
            msg.fail(err, exits=1)
        cmd = f"git -C {tmp_dir} fetch-pack {git_repo} {missings}"
        run_command(cmd, capture=True)
        # And finally, we can checkout our subpath
        cmd = f"git -C {tmp_dir} checkout {branch} {subpath}"
        run_command(cmd, capture=True)

        # Get a subdirectory of the cloned path, if appropriate
        source_path = tmp_dir / Path(subpath)
        if not is_subpath_of(tmp_dir, source_path):
            err = f"'{subpath}' is a path outside of the cloned repository."
            msg.fail(err, repo, exits=1)

        shutil.move(str(source_path), str(dest))


def git_repo_branch_exists(repo: str, branch: str) -> bool:
    """Uses 'git ls-remote' to check if a repository and branch exists

    repo (str): URL to get repo.
    branch (str): Branch on repo to check.
    RETURNS (bool): True if repo:branch exists.
    """
    get_git_version()
    cmd = f"git ls-remote {repo} {branch}"
    # We might be tempted to use `--exit-code` with `git ls-remote`, but
    # `run_command` handles the `returncode` for us, so we'll rely on
    # the fact that stdout returns '' if the requested branch doesn't exist
    ret = run_command(cmd, capture=True)
    exists = ret.stdout != ""
    return exists


def get_git_version(
    error: str = "Could not run 'git'. Make sure it's installed and the executable is available.",
) -> Tuple[int, int]:
    """Get the version of git and raise an error if calling 'git --version' fails.

    error (str): The error message to show.
    RETURNS (Tuple[int, int]): The version as a (major, minor) tuple. Returns
        (0, 0) if the version couldn't be determined.
    """
    try:
        ret = run_command("git --version", capture=True)
    except:
        raise RuntimeError(error)
    stdout = ret.stdout.strip()
    if not stdout or not stdout.startswith("git version"):
        return 0, 0
    version = stdout[11:].strip().split(".")
    return int(version[0]), int(version[1])


def _http_to_git(repo: str) -> str:
    if repo.startswith("http://"):
        repo = repo.replace(r"http://", r"https://")
    if repo.startswith(r"https://"):
        repo = repo.replace("https://", "git@").replace("/", ":", 1)
        if repo.endswith("/"):
            repo = repo[:-1]
        repo = f"{repo}.git"
    return repo


def is_subpath_of(parent, child):
    """
    Check whether `child` is a path contained within `parent`.
    """
    # Based on https://stackoverflow.com/a/37095733 .

    # In Python 3.9, the `Path.is_relative_to()` method will supplant this, so
    # we can stop using crusty old os.path functions.
    parent_realpath = os.path.realpath(parent)
    child_realpath = os.path.realpath(child)
    return os.path.commonpath([parent_realpath, child_realpath]) == parent_realpath


@overload
def string_to_list(value: str, intify: Literal[False] = ...) -> List[str]:
    ...


@overload
def string_to_list(value: str, intify: Literal[True]) -> List[int]:
    ...


def string_to_list(value: str, intify: bool = False) -> Union[List[str], List[int]]:
    """Parse a comma-separated string to a list and account for various
    formatting options. Mostly used to handle CLI arguments that take a list of
    comma-separated values.

    value (str): The value to parse.
    intify (bool): Whether to convert values to ints.
    RETURNS (Union[List[str], List[int]]): A list of strings or ints.
    """
    if not value:
        return []  # type: ignore[return-value]
    if value.startswith("[") and value.endswith("]"):
        value = value[1:-1]
    result = []
    for p in value.split(","):
        p = p.strip()
        if p.startswith("'") and p.endswith("'"):
            p = p[1:-1]
        if p.startswith('"') and p.endswith('"'):
            p = p[1:-1]
        p = p.strip()
        if intify:
            p = int(p)  # type: ignore[assignment]
        result.append(p)
    return result


def setup_gpu(use_gpu: int, silent=None) -> None:
    """Configure the GPU and log info."""
    if silent is None:
        local_msg = Printer()
    else:
        local_msg = Printer(no_print=silent, pretty=not silent)
    if use_gpu >= 0:
        local_msg.info(f"Using GPU: {use_gpu}")
        require_gpu(use_gpu)
    else:
        local_msg.info("Using CPU")
        if gpu_is_available():
            local_msg.info("To switch to GPU 0, use the option: --gpu-id 0")


def _format_number(number: Union[int, float], ndigits: int = 2) -> str:
    """Formats a number (float or int) rounding to `ndigits`, without truncating trailing 0s,
    as happens with `round(number, ndigits)`"""
    if isinstance(number, float):
        return f"{number:.{ndigits}f}"
    else:
        return str(number)
