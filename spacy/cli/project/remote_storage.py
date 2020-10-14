from typing import Optional, List, Dict, TYPE_CHECKING
import os
import site
import hashlib
import urllib.parse
import tarfile
from pathlib import Path

from .._util import get_hash, get_checksum, download_file, ensure_pathy
from ...util import make_tempdir, get_minor_version, ENV_VARS, check_bool_env_var
from ...git_info import GIT_VERSION
from ... import about

if TYPE_CHECKING:
    from pathy import Pathy  # noqa: F401


class RemoteStorage:
    """Push and pull outputs to and from a remote file storage.

    Remotes can be anything that `smart-open` can support: AWS, GCS, file system,
    ssh, etc.
    """

    def __init__(self, project_root: Path, url: str, *, compression="gz"):
        self.root = project_root
        self.url = ensure_pathy(url)
        self.compression = compression

    def push(self, path: Path, command_hash: str, content_hash: str) -> "Pathy":
        """Compress a file or directory within a project and upload it to a remote
        storage. If an object exists at the full URL, nothing is done.

        Within the remote storage, files are addressed by their project path
        (url encoded) and two user-supplied hashes, representing their creation
        context and their file contents. If the URL already exists, the data is
        not uploaded. Paths are archived and compressed prior to upload.
        """
        loc = self.root / path
        if not loc.exists():
            raise IOError(f"Cannot push {loc}: does not exist.")
        url = self.make_url(path, command_hash, content_hash)
        if url.exists():
            return None
        tmp: Path
        with make_tempdir() as tmp:
            tar_loc = tmp / self.encode_name(str(path))
            mode_string = f"w:{self.compression}" if self.compression else "w"
            with tarfile.open(tar_loc, mode=mode_string) as tar_file:
                tar_file.add(str(loc), arcname=str(path))
            with tar_loc.open(mode="rb") as input_file:
                with url.open(mode="wb") as output_file:
                    output_file.write(input_file.read())
        return url

    def pull(
        self,
        path: Path,
        *,
        command_hash: Optional[str] = None,
        content_hash: Optional[str] = None,
    ) -> Optional["Pathy"]:
        """Retrieve a file from the remote cache. If the file already exists,
        nothing is done.

        If the command_hash and/or content_hash are specified, only matching
        results are returned. If no results are available, an error is raised.
        """
        dest = self.root / path
        if dest.exists():
            return None
        url = self.find(path, command_hash=command_hash, content_hash=content_hash)
        if url is None:
            return url
        else:
            # Make sure the destination exists
            if not dest.parent.exists():
                dest.parent.mkdir(parents=True)
            tmp: Path
            with make_tempdir() as tmp:
                tar_loc = tmp / url.parts[-1]
                download_file(url, tar_loc)
                mode_string = f"r:{self.compression}" if self.compression else "r"
                with tarfile.open(tar_loc, mode=mode_string) as tar_file:
                    # This requires that the path is added correctly, relative
                    # to root. This is how we set things up in push()
                    tar_file.extractall(self.root)
        return url

    def find(
        self,
        path: Path,
        *,
        command_hash: Optional[str] = None,
        content_hash: Optional[str] = None,
    ) -> Optional["Pathy"]:
        """Find the best matching version of a file within the storage,
        or `None` if no match can be found. If both the creation and content hash
        are specified, only exact matches will be returned. Otherwise, the most
        recent matching file is preferred.
        """
        name = self.encode_name(str(path))
        if command_hash is not None and content_hash is not None:
            url = self.make_url(path, command_hash, content_hash)
            urls = [url] if url.exists() else []
        elif command_hash is not None:
            urls = list((self.url / name / command_hash).iterdir())
        else:
            urls = list((self.url / name).iterdir())
            if content_hash is not None:
                urls = [url for url in urls if url.parts[-1] == content_hash]
        return urls[-1] if urls else None

    def make_url(self, path: Path, command_hash: str, content_hash: str) -> "Pathy":
        """Construct a URL from a subpath, a creation hash and a content hash."""
        return self.url / self.encode_name(str(path)) / command_hash / content_hash

    def encode_name(self, name: str) -> str:
        """Encode a subpath into a URL-safe name."""
        return urllib.parse.quote_plus(name)


def get_content_hash(loc: Path) -> str:
    return get_checksum(loc)


def get_command_hash(
    site_hash: str, env_hash: str, deps: List[Path], cmd: List[str]
) -> str:
    """Create a hash representing the execution of a command. This includes the
    currently installed packages, whatever environment variables have been marked
    as relevant, and the command.
    """
    check_commit = check_bool_env_var(ENV_VARS.PROJECT_USE_GIT_VERSION)
    spacy_v = GIT_VERSION if check_commit else get_minor_version(about.__version__)
    dep_checksums = [get_checksum(dep) for dep in sorted(deps)]
    hashes = [spacy_v, site_hash, env_hash] + dep_checksums
    hashes.extend(cmd)
    creation_bytes = "".join(hashes).encode("utf8")
    return hashlib.md5(creation_bytes).hexdigest()


def get_site_hash():
    """Hash the current Python environment's site-packages contents, including
    the name and version of the libraries. The list we're hashing is what
    `pip freeze` would output.
    """
    site_dirs = site.getsitepackages()
    if site.ENABLE_USER_SITE:
        site_dirs.extend(site.getusersitepackages())
    packages = set()
    for site_dir in site_dirs:
        site_dir = Path(site_dir)
        for subpath in site_dir.iterdir():
            if subpath.parts[-1].endswith("dist-info"):
                packages.add(subpath.parts[-1].replace(".dist-info", ""))
    package_bytes = "".join(sorted(packages)).encode("utf8")
    return hashlib.md5sum(package_bytes).hexdigest()


def get_env_hash(env: Dict[str, str]) -> str:
    """Construct a hash of the environment variables that will be passed into
    the commands.

    Values in the env dict may be references to the current os.environ, using
    the syntax $ENV_VAR to mean os.environ[ENV_VAR]
    """
    env_vars = {}
    for key, value in env.items():
        if value.startswith("$"):
            env_vars[key] = os.environ.get(value[1:], "")
        else:
            env_vars[key] = value
    return get_hash(env_vars)
