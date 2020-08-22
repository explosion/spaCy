from pathlib import Path
from wasabi import msg
from .remote_storage import RemoteStorage
from .remote_storage import get_command_hash
from .._util import project_cli, Arg
from .._util import load_project_config, substitute_project_variables


@project_cli.command("pull")
def project_pull_cli(
    # fmt: off
    remote: str = Arg("default", help="Name or path of remote storage"),
    project_dir: Path = Arg(Path.cwd(), help="Location of project directory. Defaults to current working directory.", exists=True, file_okay=False),
    # fmt: on
):
    """Retrieve any precomputed outputs from a remote storage that are available.
    You can alias remotes in your project.yml by mapping them to storage paths.
    A storage can be anything that the smart-open library can upload to, e.g.
    gcs, aws, ssh, local directories etc
    """
    for url, output_path in project_pull(project_dir, remote):
        msg.good(f"Pulled {output_path} from {url}")


def project_pull(project_dir: Path, remote: str, *, verbose: bool=False):
    config = substitute_project_variables(load_project_config(project_dir))
    if remote in config.get("remotes", {}):
        remote = config["remotes"][remote]
    storage = RemoteStorage(project_dir, remote)
    for cmd in config.get("commands", []):
        deps = [project_dir / dep for dep in cmd.get("deps", [])]
        cmd_hash = get_command_hash("", "", deps, cmd["script"])
        for output_path in cmd.get("outputs", []):
            url = storage.pull(output_path, command_hash=cmd_hash)
            if url is not None:
                yield url, output_path
