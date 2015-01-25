from os import path
import os
import tarfile
import shutil
import wget

PARSER_URL = 'http://s3-us-west-1.amazonaws.com/media.spacynlp.com/en_deps-0.30.tgz'


DEP_VECTORS_URL = 'http://s3-us-west-1.amazonaws.com/media.spacynlp.com/vec.bin'

DEST_DIR = path.join(path.dirname(__file__), 'data')

def download_file(url, out):
    wget.download(url, out=out)

def install_parser_model(url, dest_dir):
    download_file(url, dest_dir)
    t = tarfile.open(path.join(DEST_DIR, 'en_deps-0.30.tgz'), mode=":gz")
    t.extractall(dest_dir)


def install_dep_vectors(url, dest_dir):
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)
    
    filename = download_file(url, dest_dir)


def main():
    install_parser_model(PARSER_URL, DEST_DIR)
    install_dep_vectors(DEP_VECTORS_URL, path.join(DEST_DIR, 'vocab'))


if __name__ == '__main__':
    main()
