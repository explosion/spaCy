from ..remote_cache import RemoteStorage
from ..remote_cache import get_site_hash, get_env_hash, get_command_hash


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
    project_pull(project_dir, remote)


def project_pull(project_dir: Path, remote: str):
    config = load_project_config(project_dir)
    if remote in config.get("remotes", {}):
        remote = config["remotes"][remote]
    storage = RemoteStorage(project_dir, remote)
    site_hash = get_site_hash()
    env_hash = get_env_hash(config.get("env", {}))
    for cmd in config.get("commands", []):
        deps = [project_dir / dep for dep in cmd.get("deps", [])]
        cmd_hash = get_command_hash(site_hash, env_hash, deps, cmd["script"])
        for output_path in cmd.get("outputs", []):
            url = storage.pull(output_path, command_hash=command_hash)
            if url is not None:
                print(f"Pulled {output_path} from {url}")
