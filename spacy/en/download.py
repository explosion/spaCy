from __future__ import print_function
from os import path
import sys
import os
import tarfile
import shutil
import uget
import plac

# TODO: Read this from the same source as the setup
VERSION = '0.9.5'

AWS_STORE = 'https://s3-us-west-1.amazonaws.com/media.spacynlp.com'

ALL_DATA_DIR_URL = '%s/en_data_all-%s.tgz' % (AWS_STORE, VERSION)

DEST_DIR = path.join(path.dirname(path.abspath(__file__)), 'data')


def download_file(url, dest_dir):
    return uget.download(url, dest_dir, console=sys.stdout)


def install_data(url, dest_dir):
    filename = download_file(url, dest_dir)
    t = tarfile.open(filename)
    t.extractall(dest_dir)


def install_parser_model(url, dest_dir):
    filename = download_file(url, dest_dir)
    t = tarfile.open(filename, mode=":gz")
    t.extractall(dest_dir)


def install_dep_vectors(url, dest_dir):
    download_file(url, dest_dir)


@plac.annotations(
    force=("Force overwrite", "flag", "f", bool),
)
def main(data_size='all', force=False):
    if data_size == 'all':
        data_url = ALL_DATA_DIR_URL
    elif data_size == 'small':
        data_url = SM_DATA_DIR_URL

    if force and path.exists(DEST_DIR):
        shutil.rmtree(DEST_DIR)

    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)

    install_data(data_url, DEST_DIR)


if __name__ == '__main__':
    plac.call(main)
