from os import path
import os
import tarfile
import shutil
import requests

PARSER_URL = 'http://s3-us-west-1.amazonaws.com/media.spacynlp.com/en.tgz'

DEP_VECTORS_URL = 'http://u.cs.biu.ac.il/~yogo/data/syntemb/deps.words.bz2'

DEST_DIR = path.join(path.dirname(__file__), 'data')

def download_file(url):
    local_filename = url.split('/')[-1]
    return path.join(DEST_DIR, local_filename)
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    print "Download %s" % url
    i = 0
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()
        print i
        i += 1
    return local_filename

def install_parser_model(url, dest_dir):
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)
    assert not path.exists(path.join(dest_dir, 'en'))

    filename = download_file(url)
    t = tarfile.open(filename, mode=":gz")
    t.extractall(dest_dir)
    shutil.move(path.join(dest_dir, 'en', 'deps', 'model'), dest_dir)
    shutil.move(path.join(dest_dir, 'en', 'deps', 'config.json'), dest_dir)
    shutil.rmtree(path.join(dest_dir, 'en'))


def install_dep_vectors(url, dest_dir):
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)
    
    filename = download_file(url)
    shutil.move(filename, path.join(dest_dir, 'vec.bz2'))


def main():
    #install_parser_model(PARSER_URL, path.join(DEST_DIR, 'deps'))
    install_dep_vectors(DEP_VECTORS_URL, path.join(DEST_DIR, 'vocab'))


if __name__ == '__main__':
    main()
