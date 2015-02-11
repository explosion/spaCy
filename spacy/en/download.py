from __future__ import print_function
from os import path
import os
import tarfile
import shutil
import wget
import plac

# TODO: Read this from the same source as the setup
VERSION = '0.6'

AWS_STORE = 'http://s3-us-west-1.amazonaws.com/media.spacynlp.com'

ALL_DATA_DIR_URL = '%s/en_data_all-%s.tgz' % (AWS_STORE, VERSION)

SM_DATA_DIR_URL = '%s/en_data_sm-%s.tgz' % (AWS_STORE, VERSION)

SPEECH_DATA_DIR_URL = '%s/en_data_speech-%s.tgz' % (AWS_STORE, VERSION)


DEST_DIR = path.join(path.dirname(__file__), 'data')

def download_file(url, out):
    wget.download(url, out=out)
    return url.rsplit('/', 1)[1]


def install_data(url, dest_dir):
    filename = download_file(url, dest_dir)
    t = tarfile.open(path.join(dest_dir, filename))
    t.extractall(dest_dir)

def install_parser_model(url, dest_dir):
    filename = download_file(url, dest_dir)
    t = tarfile.open(path.join(dest_dir, filename), mode=":gz")
    t.extractall(path.dirname(__file__))


def install_dep_vectors(url, dest_dir):
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)
    
    filename = download_file(url, dest_dir)


def main(data_size='all'):
    if data_size == 'all':
        data_url = ALL_DATA_DIR_URL
    elif data_size == 'speech':
        data_url = SPEECH_DATA_DIR_URL
    elif data_size == 'small':
        data_url = SM_DATA_DIR_URL
    if path.exists(DEST_DIR):
        print("Moving existing dir %s to /tmp" % DEST_DIR)
        shutil.move(DEST_DIR, '/tmp')
    install_data(data_url, path.dirname(DEST_DIR))


if __name__ == '__main__':
    plac.call(main)
