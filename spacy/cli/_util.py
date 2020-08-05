from typing import Dict, Any, Union, List, Optional
from pathlib import Path
from wasabi import msg
import srsly
import hashlib
import typer
from typer.main import get_command
from contextlib import contextmanager
from thinc.config import Config, ConfigValidationError
from configparser import InterpolationError
import sys

from ..schemas import ProjectConfigSchema, validate
from ..util import import_file


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
INIT_HELP = """Commands for initializing configs and models."""

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
    # Ensure that the help messages always display the correct prompt
    command = get_command(app)
    command(prog_name=COMMAND)


def parse_config_overrides(args: List[str]) -> Dict[str, Any]:
    """Generate a dictionary of config overrides based on the extra arguments
    provided on the CLI, e.g. --training.batch_size to override
    "training.batch_size". Arguments without a "." are considered invalid,
    since the config only allows top-level sections to exist.

    args (List[str]): The extra arguments from the command line.
    RETURNS (Dict[str, Any]): The parsed dict, keyed by nested config setting.
    """
    result = {}
    while args:
        opt = args.pop(0)
        err = f"Invalid CLI argument '{opt}'"
        if opt.startswith("--"):  # new argument
            opt = opt.replace("--", "").replace("-", "_")
            if "." not in opt:
                msg.fail(f"{err}: can't override top-level section", exits=1)
            if "=" in opt:  # we have --opt=value
                opt, value = opt.split("=", 1)
            else:
                if not args or args[0].startswith("--"):  # flag with no value
                    value = "true"
                else:
                    value = args.pop(0)
            # Just like we do in the config, we're calling json.loads on the
            # values. But since they come from the CLI, it'd be unintuitive to
            # explicitly mark strings with escaped quotes. So we're working
            # around that here by falling back to a string if parsing fails.
            # TODO: improve logic to handle simple types like list of strings?
            try:
                result[opt] = srsly.json_loads(value)
            except ValueError:
                result[opt] = str(value)
        else:
            msg.fail(f"{err}: override option should start with --", exits=1)
    return result


def load_project_config(path: Path) -> Dict[str, Any]:
    """Load the project.yml file from a directory and validate it. Also make
    sure that all directories defined in the config exist.

    path (Path): The path to the project directory.
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
        msg.fail(invalid_err, "\n".join(errors), exits=1)
    validate_project_commands(config)
    # Make sure directories defined in config exist
    for subdir in config.get("directories", []):
        dir_path = path / subdir
        if not dir_path.exists():
            dir_path.mkdir(parents=True)
    return config


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


def get_hash(data) -> str:
    """Get the hash for a JSON-serializable object.

    data: The data to hash.
    RETURNS (str): The hash.
    """
    data_str = srsly.json_dumps(data, sort_keys=True).encode("utf8")
    return hashlib.md5(data_str).hexdigest()


def get_checksum(path: Union[Path, str]) -> str:
    """Get the checksum for a file or directory given its file path. If a
    directory path is provided, this uses all files in that directory.

    path (Union[Path, str]): The file or directory path.
    RETURNS (str): The checksum.
    """
    path = Path(path)
    if path.is_file():
        return hashlib.md5(Path(path).read_bytes()).hexdigest()
    if path.is_dir():
        # TODO: this is currently pretty slow
        dir_checksum = hashlib.md5()
        for sub_file in sorted(fp for fp in path.rglob("*") if fp.is_file()):
            dir_checksum.update(sub_file.read_bytes())
        return dir_checksum.hexdigest()
    raise ValueError(f"Can't get checksum for {path}: not a file or directory")


@contextmanager
def show_validation_error(
    file_path: Optional[Union[str, Path]] = None,
    *,
    title: str = "Config validation error",
    hint_init: bool = True,
):
    """Helper to show custom config validation errors on the CLI.

    file_path (str / Path): Optional file path of config file, used in hints.
    title (str): Title of the custom formatted error.
    hint_init (bool): Show hint about filling config.
    """
    try:
        yield
    except (ConfigValidationError, InterpolationError) as e:
        msg.fail(title, spaced=True)
        # TODO: This is kinda hacky and we should probably provide a better
        # helper for this in Thinc
        err_text = str(e).replace("Config validation error", "").strip()
        print(err_text)
        if hint_init and "field required" in err_text:
            config_path = file_path if file_path is not None else "config.cfg"
            msg.text(
                "If your config contains missing values, you can run the 'init "
                "config' command to fill in all the defaults, if possible:",
                spaced=True,
            )
            print(f"{COMMAND} init config {config_path} --base {config_path}\n")
        sys.exit(1)


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


def get_sourced_components(config: Union[Dict[str, Any], Config]) -> List[str]:
    """RETURNS (List[str]): All sourced components in the original config,
        e.g. {"source": "en_core_web_sm"}. If the config contains a key
        "factory", we assume it refers to a component factory.
    """
    return [
        name
        for name, cfg in config.get("components", {}).items()
        if "factory" not in cfg and "source" in cfg
    ]
