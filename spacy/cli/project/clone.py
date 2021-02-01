from typing import Optional
from pathlib import Path
from wasabi import msg
import subprocess
import re

from ... import about
from ...util import ensure_path
from .._util import project_cli, Arg, Opt, COMMAND, PROJECT_FILE
from .._util import git_checkout, get_git_version

DEFAULT_REPO = about.__projects__
DEFAULT_PROJECTS_BRANCH = about.__projects_branch__
DEFAULT_BRANCH = "master"


@project_cli.command("clone")
def project_clone_cli(
    # fmt: off
    name: str = Arg(..., help="The name of the template to clone"),
    dest: Optional[Path] = Arg(None, help="Where to clone the project. Defaults to current working directory", exists=False),
    repo: str = Opt(DEFAULT_REPO, "--repo", "-r", help="The repository to clone from"),
    branch: Optional[str] = Opt(None, "--branch", "-b", help="The branch to clone from"),
    sparse_checkout: bool = Opt(False, "--sparse", "-S", help="Use sparse Git checkout to only check out and clone the files needed. Requires Git v22.2+.")
    # fmt: on
):
    """Clone a project template from a repository. Calls into "git" and will
    only download the files from the given subdirectory. The GitHub repo
    defaults to the official spaCy template repo, but can be customized
    (including using a private repo).

    DOCS: https://spacy.io/api/cli#project-clone
    """
    if dest is None:
        dest = Path.cwd() / Path(name).parts[-1]
    if branch is None:
        # If it's a user repo, we want to default to other branch
        branch = DEFAULT_PROJECTS_BRANCH if repo == DEFAULT_REPO else DEFAULT_BRANCH
    project_clone(name, dest, repo=repo, branch=branch, sparse_checkout=sparse_checkout)


def project_clone(
    name: str,
    dest: Path,
    *,
    repo: str = about.__projects__,
    branch: str = about.__projects_branch__,
    sparse_checkout: bool = False,
) -> None:
    """Clone a project template from a repository.

    name (str): Name of subdirectory to clone.
    dest (Path): Destination path of cloned project.
    repo (str): URL of Git repo containing project templates.
    branch (str): The branch to clone from
    """
    dest = ensure_path(dest)
    check_clone(name, dest, repo)
    project_dir = dest.resolve()
    repo_name = re.sub(r"(http(s?)):\/\/github.com/", "", repo)
    try:
        git_checkout(repo, name, dest, branch=branch, sparse=sparse_checkout)
    except subprocess.CalledProcessError:
        err = f"Could not clone '{name}' from repo '{repo_name}'"
        msg.fail(err, exits=1)
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
    git_err = (
        f"Cloning spaCy project templates requires Git and the 'git' command. ",
        f"To clone a project without Git, copy the files from the '{name}' "
        f"directory in the {repo} to {dest} manually.",
    )
    get_git_version(error=git_err)
    if not dest:
        msg.fail(f"Not a valid directory to clone project: {dest}", exits=1)
    if dest.exists():
        # Directory already exists (not allowed, clone needs to create it)
        msg.fail(f"Can't clone project, directory already exists: {dest}", exits=1)
    if not dest.parent.exists():
        # We're not creating parents, parent dir should exist
        msg.fail(
            f"Can't clone project, parent directory doesn't exist: {dest.parent}. "
            f"Create the necessary folder(s) first before continuing.",
            exits=1,
        )
