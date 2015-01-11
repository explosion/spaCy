from os import path
import os
import tarfile
import shutil
import requests

PARSER_URL = 'https://s3-us-west-1.amazonaws.com/media.spacynlp.com/en.tgz'

DEST_DIR = path.join(path.dirname(__file__), 'data', 'deps')

def download_file(url):
    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()
    return local_filename

def main():
    if not os.path.exists(DEST_DIR):
        os.mkdir(DEST_DIR)
    assert not path.exists(path.join(DEST_DIR, 'en'))


    filename = download_file(URL)
    t = tarfile.open(filename, mode=":gz")
    t.extractall(DEST_DIR)
    shutil.move(path.join(DEST_DIR, 'en', 'deps', 'model'), DEST_DIR)
    shutil.move(path.join(DEST_DIR, 'en', 'deps', 'config.json'), DEST_DIR)
    shutil.rmtree(path.join(DEST_DIR, 'en'))


if __name__ == '__main__':
    main()
