from typing import Optional
from pathlib import Path
from wasabi import msg
import subprocess
import shutil
import re

from ... import about
from ...util import ensure_path, run_command, make_tempdir
from .._app import project_cli, Arg, Opt, COMMAND
from .util import PROJECT_FILE


@project_cli.command("clone")
def project_clone_cli(
    # fmt: off
    name: str = Arg(..., help="The name of the template to clone"),
    dest: Optional[Path] = Arg(None, help="Where to clone the project. Defaults to current working directory", exists=False),
    repo: str = Opt(about.__projects__, "--repo", "-r", help="The repository to clone from"),
    # fmt: on
):
    """Clone a project template from a repository. Calls into "git" and will
    only download the files from the given subdirectory. The GitHub repo
    defaults to the official spaCy template repo, but can be customized
    (including using a private repo).
    """
    if dest is None:
        dest = Path.cwd() / name
    project_clone(name, dest, repo=repo)


def project_clone(name: str, dest: Path, *, repo: str = about.__projects__) -> None:
    """Clone a project template from a repository.

    name (str): Name of subdirectory to clone.
    dest (Path): Destination path of cloned project.
    repo (str): URL of Git repo containing project templates.
    """
    dest = ensure_path(dest)
    check_clone(name, dest, repo)
    project_dir = dest.resolve()
    repo_name = re.sub(r"(http(s?)):\/\/github.com/", "", repo)
    # We're using Git and sparse checkout to only clone the files we need
    with make_tempdir() as tmp_dir:
        cmd = f"git clone {repo} {tmp_dir} --no-checkout --depth 1 --config core.sparseCheckout=true"
        try:
            run_command(cmd)
        except subprocess.CalledProcessError:
            err = f"Could not clone the repo '{repo}' into the temp dir '{tmp_dir}'."
            msg.fail(err)
        with (tmp_dir / ".git" / "info" / "sparse-checkout").open("w") as f:
            f.write(name)
        try:
            run_command(["git", "-C", str(tmp_dir), "fetch"])
            run_command(["git", "-C", str(tmp_dir), "checkout"])
        except subprocess.CalledProcessError:
            err = f"Could not clone '{name}' from repo '{repo_name}'"
            msg.fail(err)
        # We need Path(name) to make sure we also support subdirectories
        shutil.move(str(tmp_dir / Path(name)), str(project_dir))
    msg.good(f"Cloned '{name}' from {repo_name}", project_dir)
    if not (project_dir / PROJECT_FILE).exists():
        msg.warn(f"No {PROJECT_FILE} found in directory")
    else:
        msg.good(f"Your project is now ready!")
        print(f"To fetch the assets, run:\n{COMMAND} project assets {dest}")


def check_clone(name: str, dest: Path, repo: str) -> None:
    """Check and validate that the destination path can be used to clone. Will
    check that Git is available and that the destination path is suitable.

    name (str): Name of the directory to clone from the repo.
    dest (Path): Local destination of cloned directory.
    repo (str): URL of the repo to clone from.
    """
    try:
        subprocess.run(["git", "--version"], stdout=subprocess.DEVNULL)
    except Exception:
        msg.fail(
            f"Cloning spaCy project templates requires Git and the 'git' command. ",
            f"To clone a project without Git, copy the files from the '{name}' "
            f"directory in the {repo} to {dest} manually and then run:",
            f"{COMMAND} project init {dest}",
            exits=1,
        )
    if not dest:
        msg.fail(f"Not a valid directory to clone project: {dest}", exits=1)
    if dest.exists():
        # Directory already exists (not allowed, clone needs to create it)
        msg.fail(f"Can't clone project, directory already exists: {dest}", exits=1)
    if not dest.parent.exists():
        # We're not creating parents, parent dir should exist
        msg.fail(
            f"Can't clone project, parent directory doesn't exist: {dest.parent}",
            exits=1,
        )
