from .utils import url_exists, url_join, download_file


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
    env_sig = get_env_signature(project_dir)
    for cmd in config.get("commands", []):
        for output_path in cmd.get("outputs", []):
            output_loc = project_dir / output_path
            if not output_loc.exists():
                url = url_join(get_url_parts(remote, output_path, cmd_sig))
                if url_exists(url):
                    download_file(url_join(url_parts), output_loc)
