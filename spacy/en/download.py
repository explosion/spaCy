from __future__ import print_function
import sys
import os
import tarfile
import shutil
import plac

from . import uget


try:
    FileExistsError
except NameError:
    FileExistsError = Exception


# TODO: Read this from the same source as the setup
VERSION = '0.9.6'

AWS_STORE = 'https://s3-us-west-1.amazonaws.com/media.spacynlp.com'

ALL_DATA_DIR_URL = '%s/en_data_all-%s.tgz' % (AWS_STORE, VERSION)

DEST_DIR = os.path.dirname(os.path.abspath(__file__))


def download_file(url, download_path):
    return uget.download(url, download_path, console=sys.stdout)


def install_data(url, extract_path, download_path):
    try:
        os.makedirs(extract_path)
    except FileExistsError:
        pass

    tmp = download_file(url, download_path)
    assert tmp == download_path
    t = tarfile.open(download_path)
    t.extractall(extract_path)


@plac.annotations(
    force=("Force overwrite", "flag", "f", bool),
)
def main(data_size='all', force=False):
    filename = ALL_DATA_DIR_URL.rsplit('/', 1)[1]
    download_path = os.path.join(DEST_DIR, filename)
    data_path = os.path.join(DEST_DIR, 'data')

    if force and os.path.exists(download_path):
        os.unlink(download_path)

    if force and os.path.exists(data_path):
        shutil.rmtree(data_path)

    if os.path.exists(data_path):
        print('data already installed at %s, overwrite with --force' % DEST_DIR)
        sys.exit(1)

    install_data(ALL_DATA_DIR_URL, DEST_DIR, download_path)


if __name__ == '__main__':
    plac.call(main)
