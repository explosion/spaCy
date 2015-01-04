from fabric.api import local, run, lcd, cd, env
from os.path import exists as file_exists
from fabtools.python import install, is_installed, virtualenv, install_requirements
from os import path
import json


PWD = path.dirname(__file__)
VENV_DIR = path.join(PWD, '.env')
DEV_ENV_DIR = path.join(PWD, '.denv')


def require_dep(name):
    local('pip install %s' % name)


def dev():
    # Allow this to persist, since we aren't as rigorous about keeping state clean
    if not file_exists('.denv'):
        local('virtualenv .denv')
 
    with virtualenv(DEV_ENV_DIR):
        require_dep('cython')
        require_dep('murmurhash')
        require_dep('numpy')
        local('pip install -r requirements.txt')


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


def setup():
    if file_exists('.env'):
        local('rm -rf .env')
    local('virtualenv .env')
    with virtualenv(VENV_DIR):
        local('pip install --upgrade setuptools')


def install():
    with virtualenv(VENV_DIR):
        local('pip install dist/*.tar.gz')
        local('pip install pytest')


def make():
    with virtualenv(DEV_ENV_DIR):
        with lcd(path.dirname(__file__)):
            local('python dev_setup.py build_ext --inplace > /dev/null')


def vmake():
    with virtualenv(VENV_DIR):
        with lcd(path.dirname(__file__)):
            local('python dev_setup.py build_ext --inplace')



def clean():
    with lcd(path.dirname(__file__)):
        local('python dev_setup.py clean --all')


def test():
    with virtualenv(VENV_DIR):
        with lcd(path.dirname(__file__)):
            local('py.test -x')


def clean():
    local('python setup.py clean --all')


def docs():
    with lcd('docs'):
        local('make html')


def pos():
    local('rm -rf data/en/pos')
    local('python tools/train.py pos ~/work_data/docparse/wsj02-21.conll data/en/pos')
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
