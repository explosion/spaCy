from pathlib import Path
from wasabi import msg
from .remote_storage import RemoteStorage
from .remote_storage import get_command_hash
from .._util import project_cli, Arg, logger
from .._util import load_project_config
from .run import update_lockfile


@project_cli.command("pull")
def project_pull_cli(
    # fmt: off
    remote: str = Arg("default", help="Name or path of remote storage"),
    project_dir: Path = Arg(Path.cwd(), help="Location of project directory. Defaults to current working directory.", exists=True, file_okay=False),
    # fmt: on
):
    """Retrieve available precomputed outputs from a remote storage.
    You can alias remotes in your project.yml by mapping them to storage paths.
    A storage can be anything that the smart-open library can upload to, e.g.
    AWS, Google Cloud Storage, SSH, local directories etc.

    DOCS: https://spacy.io/api/cli#project-pull
    """
    for url, output_path in project_pull(project_dir, remote):
        if url is not None:
            msg.good(f"Pulled {output_path} from {url}")


def project_pull(project_dir: Path, remote: str, *, verbose: bool = False):
    # TODO: We don't have tests for this :(. It would take a bit of mockery to
    # set up. I guess see if it breaks first?
    config = load_project_config(project_dir)
    if remote in config.get("remotes", {}):
        remote = config["remotes"][remote]
    storage = RemoteStorage(project_dir, remote)
    commands = list(config.get("commands", []))
    # We use a while loop here because we don't know how the commands
    # will be ordered. A command might need dependencies from one that's later
    # in the list.
    while commands:
        for i, cmd in enumerate(list(commands)):
            logger.debug(f"CMD: {cmd['name']}.")
            deps = [project_dir / dep for dep in cmd.get("deps", [])]
            if all(dep.exists() for dep in deps):
                cmd_hash = get_command_hash("", "", deps, cmd["script"])
                for output_path in cmd.get("outputs", []):
                    url = storage.pull(output_path, command_hash=cmd_hash)
                    logger.debug(
                        f"URL: {url} for {output_path} with command hash {cmd_hash}"
                    )
                    yield url, output_path

                out_locs = [project_dir / out for out in cmd.get("outputs", [])]
                if all(loc.exists() for loc in out_locs):
                    update_lockfile(project_dir, cmd)
                # We remove the command from the list here, and break, so that
                # we iterate over the loop again.
                commands.pop(i)
                break
            else:
                logger.debug(f"Dependency missing. Skipping {cmd['name']} outputs.")
        else:
            # If we didn't break the for loop, break the while loop.
            break
