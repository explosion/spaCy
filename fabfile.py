# coding: utf-8
from __future__ import unicode_literals, print_function

import contextlib
from pathlib import Path
from fabric.api import local, lcd, env, settings, prefix
from os import path, environ
import shutil


PWD = path.dirname(__file__)
ENV = environ['VENV_DIR'] if 'VENV_DIR' in environ else '.env'
VENV_DIR = Path(PWD) / ENV


@contextlib.contextmanager
def virtualenv(name, create=False, python='/usr/bin/python3.6'):
    python = Path(python).resolve()
    env_path = VENV_DIR
    if create:
        if env_path.exists():
            shutil.rmtree(str(env_path))
        local('{python} -m venv {env_path}'.format(python=python, env_path=VENV_DIR))
    def wrapped_local(cmd, env_vars=[], capture=False, direct=False):
        return local('source {}/bin/activate && {}'.format(env_path, cmd),
                     shell='/bin/bash', capture=False)
    yield wrapped_local


def env(lang='python3.6'):
    if VENV_DIR.exists():
        local('rm -rf {env}'.format(env=VENV_DIR))
    if lang.startswith('python3'):
        local('{lang} -m venv {env}'.format(lang=lang, env=VENV_DIR))
    else:
        local('{lang} -m pip install virtualenv --no-cache-dir'.format(lang=lang))
        local('{lang} -m virtualenv {env} --no-cache-dir'.format(lang=lang, env=VENV_DIR))
    with virtualenv(VENV_DIR) as venv_local:
        print(venv_local('python --version', capture=True))
        venv_local('pip install --upgrade setuptools --no-cache-dir')
        venv_local('pip install pytest --no-cache-dir')
        venv_local('pip install wheel --no-cache-dir')
        venv_local('pip install -r requirements.txt --no-cache-dir')
        venv_local('pip install pex --no-cache-dir')



def install():
    with virtualenv(VENV_DIR) as venv_local:
        venv_local('pip install dist/*.tar.gz')


def make():
    with lcd(path.dirname(__file__)):
        local('export PYTHONPATH=`pwd` && source .env/bin/activate && python setup.py build_ext --inplace',
            shell='/bin/bash')

def sdist():
    with virtualenv(VENV_DIR) as venv_local:
        with lcd(path.dirname(__file__)):
            local('python setup.py sdist')

def wheel():
    with virtualenv(VENV_DIR) as venv_local:
        with lcd(path.dirname(__file__)):
            venv_local('python setup.py bdist_wheel')

def pex():
    with virtualenv(VENV_DIR) as venv_local:
        with lcd(path.dirname(__file__)):
            sha = local('git rev-parse --short HEAD', capture=True)
            venv_local('pex dist/*.whl -e spacy -o dist/spacy-%s.pex' % sha,
                direct=True)


def clean():
    with lcd(path.dirname(__file__)):
        local('rm -f dist/*.whl')
        local('rm -f dist/*.pex')
        with virtualenv(VENV_DIR) as venv_local:
            venv_local('python setup.py clean --all')


def test():
    with virtualenv(VENV_DIR) as venv_local:
        with lcd(path.dirname(__file__)):
            venv_local('pytest -x spacy/tests')

def train():
    args = environ.get('SPACY_TRAIN_ARGS', '')
    with virtualenv(VENV_DIR) as venv_local:
        venv_local('spacy train {args}'.format(args=args))
