from __future__ import print_function
from os import path
import sys
import os
import tarfile
import shutil
import plac

from . import uget

# TODO: Read this from the same source as the setup
VERSION = '0.9.5'

AWS_STORE = 'https://s3-us-west-1.amazonaws.com/media.spacynlp.com'

ALL_DATA_DIR_URL = '%s/en_data_all-%s.tgz' % (AWS_STORE, VERSION)

DEST_DIR = path.join(path.dirname(path.abspath(__file__)), 'data')


def download_file(url, path):
    return uget.download(url, path, console=sys.stdout)


def install_data(url, path, filename):
    try:
        os.makedirs(path)
    except FileExistsError:
        pass

    filename = download_file(url, os.path.join(path, filename))
    t = tarfile.open(filename)
    t.extractall(path)


@plac.annotations(
    force=("Force overwrite", "flag", "f", bool),
)
def main(data_size='all', force=False):
    if force and path.exists(DEST_DIR):
        shutil.rmtree(DEST_DIR)

    filename = ALL_DATA_DIR_URL.rsplit('/', 1)[1]

    if os.path.exists(DEST_DIR):
        # ugly hack to find out whether something other
        # than the currently wanted file lives there
        if len([f for f in os.listdir(DEST_DIR) if f != filename]):
            print('data already installed at %s, overwrite with --force' % DEST_DIR)
            sys.exit(1)

    install_data(ALL_DATA_DIR_URL, DEST_DIR, filename)


if __name__ == '__main__':
    plac.call(main)
