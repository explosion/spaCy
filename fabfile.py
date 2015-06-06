from fabric.api import local, lcd, env
from os.path import exists as file_exists
from fabtools.python import virtualenv
from os import path


PWD = path.dirname(__file__)
VENV_DIR = path.join(PWD, '.env')


def sdist():
    if file_exists('dist/'):
        local('rm -rf dist/')
    local('mkdir dist')
    with virtualenv(VENV_DIR):
        local('python setup.py sdist')


def publish():
    with virtualenv(VENV_DIR):
        local('python setup.py register')
        local('twine upload dist/*.tar.gz')
        local('git push origin master')


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
        # Run each test file separately. pytest is performing poorly, not sure why
        with lcd(path.dirname(__file__)):
            files = local('ls tests/test_*.py', capture=True)
            for fn in files:
                with settings(warn_only=True):
                    local('py.test -x %s' % fn)


def train(json_dir=None, dev_loc=None, model_dir=None):
    if json_dir is None:
        json_dir = 'corpora/en/json'
    if model_dir is None:
        model_dir = 'models/en/'
    with virtualenv(VENV_DIR):
        with lcd(path.dirname(__file__)):
            local('python bin/init_model.py lang_data/en/ corpora/en/ ' + model_dir)
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
