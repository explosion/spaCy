import hashlib
import os
import shutil
import sys
from configparser import InterpolationError
from contextlib import contextmanager
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Union,
    overload,
)

import srsly
import typer
from click import NoSuchOption
from click.parser import split_arg_string
from thinc.api import Config, ConfigValidationError, require_gpu
from thinc.util import gpu_is_available
from typer.main import get_command
from wasabi import Printer, msg
from weasel import app as project_cli

from .. import about
from ..compat import Literal
from ..schemas import validate
from ..util import (
    ENV_VARS,
    SimpleFrozenDict,
    import_file,
    is_compatible_version,
    logger,
    make_tempdir,
    registry,
    run_command,
)

SDIST_SUFFIX = ".tar.gz"
WHEEL_SUFFIX = "-py3-none-any.whl"

PROJECT_FILE = "project.yml"
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
BENCHMARK_HELP = """Commands for benchmarking pipelines."""
INIT_HELP = """Commands for initializing configs and pipeline packages."""

# Wrappers for Typer's annotations. Initially created to set defaults and to
# keep the names short, but not needed at the moment.
Arg = typer.Argument
Opt = typer.Option

app = typer.Typer(name=NAME, help=HELP)
benchmark_cli = typer.Typer(name="benchmark", help=BENCHMARK_HELP, no_args_is_help=True)
debug_cli = typer.Typer(name="debug", help=DEBUG_HELP, no_args_is_help=True)
init_cli = typer.Typer(name="init", help=INIT_HELP, no_args_is_help=True)

app.add_typer(project_cli, name="project", help=PROJECT_HELP, no_args_is_help=True)
app.add_typer(debug_cli)
app.add_typer(benchmark_cli)
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
        logger.debug("Config overrides from CLI: %s", keys)
    if env_overrides:
        logger.debug("Config overrides from env variables: %s", list(env_overrides))
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


def walk_directory(path: Path, suffix: Optional[str] = None) -> List[Path]:
    """Given a directory and a suffix, recursively find all files matching the suffix.
    Directories or files with names beginning with a . are ignored, but hidden flags on
    filesystems are not checked.
    When provided with a suffix `None`, there is no suffix-based filtering."""
    if not path.is_dir():
        return [path]
    paths = [path]
    locs = []
    seen = set()
    for path in paths:
        if str(path) in seen:
            continue
        seen.add(str(path))
        if path.parts[-1].startswith("."):
            continue
        elif path.is_dir():
            paths.extend(path.iterdir())
        elif suffix is not None and not path.parts[-1].endswith(suffix):
            continue
        else:
            locs.append(path)
    # It's good to sort these, in case the ordering messes up cache.
    locs.sort()
    return locs


def _format_number(number: Union[int, float], ndigits: int = 2) -> str:
    """Formats a number (float or int) rounding to `ndigits`, without truncating trailing 0s,
    as happens with `round(number, ndigits)`"""
    if isinstance(number, float):
        return f"{number:.{ndigits}f}"
    else:
        return str(number)
