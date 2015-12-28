from __future__ import print_function

from fabric.api import local, lcd, env, settings, prefix
from os.path import exists as file_exists
from fabtools.python import virtualenv
from os import path
import os
import shutil
from pathlib import Path


PWD = path.dirname(__file__)
VENV_DIR = path.join(PWD, '.env')


def counts():
    pass
    # Tokenize the corpus
    # tokenize() 
    # get_freqs()
    # Collate the counts
    # cat freqs | sort -k2 | gather_freqs()
    # gather_freqs()
    # smooth()


# clean, make, sdist
# cd to new env, install from sdist, 
# Push changes to server
# Pull changes on server
# clean make init model
# test --vectors --slow
# train
# test --vectors --slow --models
# sdist
# upload data to server
# change to clean venv
# py2: install from sdist, test --slow, download data, test --models --vectors
# py3: install from sdist, test --slow, download data, test --models --vectors


def prebuild(build_dir='/tmp/build_spacy'):
    if file_exists(build_dir):
        shutil.rmtree(build_dir)
    os.mkdir(build_dir)
    spacy_dir = path.dirname(__file__)
    wn_url = 'http://wordnetcode.princeton.edu/3.0/WordNet-3.0.tar.gz'
    build_venv = path.join(build_dir, '.env')
    with lcd(build_dir):
        local('git clone %s .' % spacy_dir)
        local('virtualenv ' + build_venv)
        with prefix('cd %s && PYTHONPATH=`pwd` && . %s/bin/activate' % (build_dir, build_venv)):
            local('pip install cython fabric fabtools pytest')
            local('pip install --no-cache-dir -r requirements.txt')
            local('fab clean make')
            local('cp -r %s/corpora/en/wordnet corpora/en/' % spacy_dir)
            local('PYTHONPATH=`pwd` python bin/init_model.py en lang_data corpora spacy/en/data')
            local('PYTHONPATH=`pwd` fab test')
            local('PYTHONPATH=`pwd` python -m spacy.en.download --force all')
            local('PYTHONPATH=`pwd` py.test --models spacy/tests/')


def web():
    def jade(source_name, out_dir):
        pwd = path.join(path.dirname(__file__), 'website')
        jade_loc = path.join(pwd, 'src', 'jade', source_name)
        out_loc = path.join(pwd, 'site', out_dir)
        local('jade -P %s --out %s' % (jade_loc, out_loc))

    with virtualenv(VENV_DIR):
        local('./website/create_code_samples spacy/tests/website/ website/src/code/')

    jade('404.jade', '')
    jade('home/index.jade', '')
    jade('docs/index.jade', 'docs/')
    jade('blog/index.jade', 'blog/')

    for collection in ('blog', 'tutorials'):
        for post_dir in (Path(__file__).parent / 'website' / 'src' / 'jade' / collection).iterdir():
            if post_dir.is_dir() \
            and (post_dir / 'index.jade').exists() \
            and (post_dir / 'meta.jade').exists():
                jade(str(post_dir / 'index.jade'), path.join(collection, post_dir.parts[-1]))


def web_publish(assets_path):
    from boto.s3.connection import S3Connection, OrdinaryCallingFormat

    site_path = 'website/site'

    os.environ['S3_USE_SIGV4'] = 'True'
    conn = S3Connection(host='s3.eu-central-1.amazonaws.com',
                        calling_format=OrdinaryCallingFormat())
    bucket = conn.get_bucket('spacy.io', validate=False)

    keys_left = set([k.name for k in bucket.list()
                     if not k.name.startswith('resources')])

    for root, dirnames, filenames in os.walk(site_path):
        for dirname in dirnames:
            target = os.path.relpath(os.path.join(root, dirname), site_path)
            source = os.path.join(target, 'index.html')

            if os.path.exists(os.path.join(root, dirname, 'index.html')):
                key = bucket.new_key(source)
                key.set_redirect('//%s/%s' % (bucket.name, target))
                print('adding redirect for %s' % target)

                keys_left.remove(source)

        for filename in filenames:
            source = os.path.join(root, filename)

            target = os.path.relpath(root, site_path)
            if target == '.':
                target = filename
            elif filename != 'index.html':
                target = os.path.join(target, filename)

            key = bucket.new_key(target)
            key.set_metadata('Content-Type', 'text/html')
            key.set_contents_from_filename(source)
            print('uploading %s' % target)

            keys_left.remove(target)

    for key_name in keys_left:
        print('deleting %s' % key_name)
        bucket.delete_key(key_name)

    local('aws s3 sync --delete %s s3://spacy.io/resources' % assets_path)


def publish(version):
    with virtualenv(VENV_DIR):
        local('git push origin master')
        local('git tag -a %s' % version)
        local('git push origin %s' % version)
        local('python setup.py sdist')
        local('python setup.py register')
        local('twine upload dist/spacy-%s.tar.gz' % version)


def env(lang="python2.7"):
    if file_exists('.env'):
        local('rm -rf .env')
    local('virtualenv -p %s .env' % lang)


def install():
    with virtualenv(VENV_DIR):
        local('pip install --upgrade setuptools')
        local('pip install dist/*.tar.gz')
        local('pip install pytest')


def make():
    with virtualenv(VENV_DIR):
        with lcd(path.dirname(__file__)):
            local('pip install cython')
            local('pip install murmurhash')
            local('pip install -r requirements.txt')
            local('python setup.py build_ext --inplace')


def clean():
    with lcd(path.dirname(__file__)):
        local('python setup.py clean --all')


def test():
    with virtualenv(VENV_DIR):
        with lcd(path.dirname(__file__)):
            local('py.test -x spacy/tests')


def train(json_dir=None, dev_loc=None, model_dir=None):
    if json_dir is None:
        json_dir = 'corpora/en/json'
    if model_dir is None:
        model_dir = 'models/en/'
    with virtualenv(VENV_DIR):
        with lcd(path.dirname(__file__)):
            local('python bin/init_model.py en lang_data/ corpora/ ' + model_dir)
            local('python bin/parser/train.py %s %s' % (json_dir, model_dir))


def travis():
    local('open https://travis-ci.org/honnibal/thinc')


def pos():
    with virtualenv(VENV_DIR):
        local('python tools/train.py ~/work_data/docparse/wsj02-21.conll ~/work_data/docparse/wsj22.conll spacy/en/data')
        local('python tools/tag.py ~/work_data/docparse/wsj22.raw /tmp/tmp')
        local('python tools/eval_pos.py ~/work_data/docparse/wsj22.conll /tmp/tmp')


def ner():
    local('rm -rf data/en/ner')
    local('python tools/train_ner.py ~/work_data/docparse/wsj02-21.conll data/en/ner')
    local('python tools/tag_ner.py ~/work_data/docparse/wsj22.raw /tmp/tmp')
    local('python tools/eval_ner.py ~/work_data/docparse/wsj22.conll /tmp/tmp | tail')


def conll():
    local('rm -rf data/en/ner')
    local('python tools/conll03_train.py ~/work_data/ner/conll2003/eng.train data/en/ner/')
    local('python tools/conll03_eval.py ~/work_data/ner/conll2003/eng.testa')
