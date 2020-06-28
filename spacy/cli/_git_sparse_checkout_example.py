import tempfile
import typer
from pathlib import Path
import subprocess
import shlex
import shutil
from contextlib import contextmanager


@contextmanager
def make_tempdir():
    d = Path(tempfile.mkdtemp())
    yield d
    shutil.rmtree(str(d))



def clone_repo(repo, temp_dir):
    subprocess.check_call([
        "git",
        "clone",
        repo,
        temp_dir,
        "--no-checkout",
        "--depth", "1",
        "--config", "core.sparseCheckout=true"
    ])


def checkout_and_fetch(temp_dir):
    subprocess.check_call([
        "git",
        "-C", temp_dir,
        "fetch"
    ])
    subprocess.check_call([
        "git",
        "-C", temp_dir,
        "checkout"
    ])


def set_sparse_checkout_dir(temp_dir, subpath):
    with (temp_dir / ".git" / "info" / "sparse-checkout").open("w") as file_:
        file_.write(subpath)


def main(repo: str, subpath: str, dest: Path):
    with make_tempdir() as temp_dir:
        clone_repo(repo, temp_dir)
        print("After clone", list(temp_dir.iterdir()))
        set_sparse_checkout_dir(temp_dir, subpath)
        checkout_and_fetch(temp_dir)
        print("After checkout", list(temp_dir.iterdir()))
        assert (temp_dir / subpath) in list(temp_dir.iterdir())
        shutil.copytree(temp_dir / subpath, dest / subpath, dirs_exist_ok=True)
    print("Exists after cleanup?", temp_dir.exists())
    print("Destination", list(dest.iterdir()))


if __name__ == "__main__":
    typer.run(main)
