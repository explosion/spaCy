from typing import Optional, List
import os
import site
import hashlib
import urllib.parse
from urllib.parse import urljoin
from pathlib import Path
from tarfile import TarFile
from .._util import get_hash
from .._util import upload_file, list_url_files, url_exists
from ...util import make_tempdir


class RemoteStorage:
    """Push and pull outputs to and from a remote file storage.
   
    Remotes can be anything that `smart-open` can support: AWS, GCS, file system,
    ssh, etc.
    """
    def __init__(self, project_root: Path, url: str, *, compression="gz"):
        self.root = project_root
        self.url = url
        self.compression = compression

    def push(self, path: Path, creation_hash: str, content_hash: str) -> str:
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
        url = self.make_url(path, creation_hash, content_hash)
        if self.has_file(path, creation_hash, content_hash):
            return url
        with make_tempdir() as tmp:
            tar_loc = tmp / self.encode_name(str(path))
            mode_string = f"w:{self.compression}" if self.compression else "w"
            tar_file = TarFile(tar_loc, mode=mode_string)
            tar_file.add(loc)
            tar_file.close()
            upload_file(tar_loc, url)
        return url

    def pull(self, path: Path, creation_hash: Optional[str], content_hash: Optional[str]) -> Path:
        """Retrieve a file from the remote cache. If the file already exists,
        nothing is done.

        If the creation_hash and/or content_hash are specified, only matching
        results are returned. If no results are available, an error is raised.
        """
        loc = self.root / path
        if loc.exists():
            return loc

    def find(
        self,
        path: Path,
        *,
        creation_hash: Optional[str]=None,
        content_hash: Optional[str]=None
    ) -> Optional[str]:
        """Find the best matching version of a file within the storage,
        or `None` if no match can be found. If both the creation and content hash
        are specified, only exact matches will be returned. Otherwise, the most
        recent matching file is preferred.
        """
        name = self.encode_name(path)
        if creation_hash is not None and content_hash is not None:
            url = self.make_url(path, creation_hash, content_hash)
            urls = [url] if url_exists(url) else []
        elif creation_hash is not None:
            urls = list_url_files(urljoin(self.remote, name, creation_hash))
        elif content_hash is not None:
            urls = list_url_files(urljoin(self.remote, name))
            urls = [url for url in urls if url.endswith(content_hash)]
        else:
            urls = list_url_files(urljoin(self.remote, name))
        return urls[-1] if urls else None

    def make_url(self, name: str, hashes: List[str]) -> str:
        encoded_name = self.encode_name(name)
        return urllib.parse.urljoin(self.base, encoded_name, *hashes)

    def encode_name(self, name: str) -> str:
        return urllib.parse.quote_plus(name)


def hash_site_packages():
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


def hash_env_vars(keys: List[str]) -> str:
    env_vars = {key: os.environ.get(key, None) for key in keys}
    return get_hash(env_vars)
