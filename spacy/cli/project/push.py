from .remote_cache import RemoteStorage
from .._util import get_checksum, combine_hashes, get_env_hash, get_command_hash


@project_cli.command("push")
def project_push_cli(
    # fmt: off
    remote: str = Arg("default", help="Name or path of remote storage"),
    project_dir: Path = Arg(Path.cwd(), help="Location of project directory. Defaults to current working directory.", exists=True, file_okay=False),
    # fmt: on
):
    """Persist outputs to a remote storage. You can alias remotes in your project.yml
    by mapping them to storage paths. A storage can be anything that the smart-open
    library can upload to, e.g. gcs, aws, ssh, local directories etc
    """
    project_push(project_dir, remote)


def project_push(project_dir: Path, remote: str):
    """Persist outputs to a remote storage. You can alias remotes in your project.yml
    by mapping them to storage paths. A storage can be anything that the smart-open
    library can upload to, e.g. gcs, aws, ssh, local directories etc
    """
    config = load_project_config(project_dir)
    if remote in config.get("remotes", {}):
        remote = config["remotes"][remote]
    storage = RemoteStorage(project_dir, remote)
    site_hash = hash_site_packages()
    env_hash = hash_env_vars(config.get("env", {}))
    for cmd in config.get("commands", []):
        cmd_hash = combine_hashes(env_sig, get_cmd_hash(project_dir, cmd))
        for output_path in cmd.get("outputs", []):
            output_loc = project_dir / output_path
            if output_loc.exists():
                storage.push(output_path, cmd_hash, get_content_hash(output_loc))
