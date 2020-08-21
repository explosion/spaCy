import base64
from tarfile import TarFile
from .utils import url_join, upload_file
from .utils import get_url_parts, combine_sigs
from .utils import get_env_signature, get_cmd_signature


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
    env_sig = get_env_signature(project_dir)
    for cmd in config.get("commands", []):
        cmd_sig = combine_sigs(env_sig, _get_cmd_signature(project_dir, cmd))
        for output_path in cmd.get("outputs", []):
            output_loc = project_dir / output_path
            if output_loc.exists():
                if output_loc.is_dir():
                    _push_directory(project_dir, output_path, cmd_sig, remote)
                else:
                    _push_file(project_dir, output_path, cmd_sig, remote)


def _push_directory(project_dir, output_path, cmd_sig, remote):
    output_loc = project_dir / output_path
    url_parts = get_url_parts(remote, output_path, cmd_sig)
    with make_tempdir() as tmp:
        tar_loc = tmp / url_parts[-1]
        tar_file = TarFile(tar_loc, mode="w:gz")
        tar_file.add(output_loc, arcname=output_path)
        tar_file.close()
        upload_file(tar_loc, url_join(url_parts))


def _push_file(project_dir, output_path, cmd_sig, remote):
    output_loc = project_dir / output_path
    url_parts = get_url_parts(remote, output_path, cmd_sig)
    upload_file(output_loc, url_join(url_parts))
