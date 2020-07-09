from typing import Dict, Any, Union
from pathlib import Path
from wasabi import msg
import srsly
import hashlib

from ...schemas import ProjectConfigSchema, validate


PROJECT_FILE = "project.yml"
PROJECT_LOCK = "project.lock"


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
