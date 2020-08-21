from typing import Optional, List
import os
import site
import hashlib
import urllib.parse
from urllib.parse import urljoin
from pathlib import Path
from pathy import Pathy
from tarfile import TarFile
from .._util import get_hash
from .._util import upload_file
from ...util import make_tempdir


class RemoteStorage:
    """Push and pull outputs to and from a remote file storage.
   
    Remotes can be anything that `smart-open` can support: AWS, GCS, file system,
    ssh, etc.
    """
    def __init__(self, project_root: Path, url: str, *, compression="gz"):
        self.root = project_root
        self.url = Pathy(url)
        self.compression = compression

    def push(self, path: Path, creation_hash: str, content_hash: str) -> Pathy:
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
        if url.exists():
            return url
        tmp: Path
        with make_tempdir() as tmp:
            tar_loc = tmp / self.encode_name(str(path))
            mode_string = f"w:{self.compression}" if self.compression else "w"
            tar_file = TarFile(tar_loc, mode=mode_string)
            tar_file.add(str(loc))
            tar_file.close()
            with tar_loc.open(mode="rb") as input_file:
                with url.open(mode="wb") as output_file:
                    output_file.write(input_file.read())
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
        return loc

    def find(
        self,
        path: Path,
        *,
        creation_hash: Optional[str]=None,
        content_hash: Optional[str]=None
    ) -> Optional[Pathy]:
        """Find the best matching version of a file within the storage,
        or `None` if no match can be found. If both the creation and content hash
        are specified, only exact matches will be returned. Otherwise, the most
        recent matching file is preferred.
        """
        name = self.encode_name(str(path))
        if creation_hash is not None and content_hash is not None:
            url = self.make_url(path, creation_hash, content_hash)
            urls = [url] if url.exists() else []
        elif creation_hash is not None:
            urls = list((self.url / name / creation_hash).iterdir())
        else:
            urls = list((self.url / name).iterdir())
            if content_hash is not None:
                urls = [url for url in urls if url.parts[-1] == content_hash]
        return urls[-1] if urls else None

    def make_url(self, path: Path, creation_hash: str, content_hash: str) -> Pathy:
        return self.url / self.encode_name(str(path)) / creation_hash / content_hash

    def encode_name(self, name: str) -> str:
        return urllib.parse.quote_plus(name)
