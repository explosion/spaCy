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
        local('{python} -m venv {env_path}'.format(python=python,
                                                   env_path=VENV_DIR))
    def wrapped_local(cmd, env_vars=[]):
        env_py = env_path / 'bin' / 'python'
        env_vars = ' '.join(env_vars)
        if cmd.split()[0] == 'python':
            cmd = cmd.replace('python', str(env_py))
            return local(env_vars + ' ' + cmd)
        else:
            return local('{env_vars} {env_py} -m {cmd}'.format(
                    env_py=env_py, cmd=cmd, env_vars=env_vars))
    yield wrapped_local


def env(lang='python3.6'):
    if VENV_DIR.exists():
        local('rm -rf {env}'.format(env=VENV_DIR))
    local('{lang} -m pip install virtualenv --no-cache-dir'.format(lang=lang))
    if lang.startswith('python3'):
        local('{lang} -m venv {env}'.format(lang=lang, env=VENV_DIR))
    else:
        local('{lang} -m virtualenv {env} --no-cache-dir'.format(lang=lang, env=VENV_DIR))
    with virtualenv(VENV_DIR) as venv_local:
        print(venv_local('python --version', capture=True))
        venv_local('pip install --upgrade setuptools --no-cache-dir')
        venv_local('pip install pytest --no-cache-dir')


def install():
    with virtualenv(VENV_DIR) as venv_local:
        venv_local('pip install dist/*.tar.gz')


def make():
    with virtualenv(VENV_DIR) as venv_local:
        with lcd(path.dirname(__file__)):
            venv_local('pip install -r requirements.txt')
            venv_local('python setup.py build_ext --inplace', env_vars=['PYTHONPATH=`pwd`'])

def sdist():
    with virtualenv(VENV_DIR) as venv_local:
        with lcd(path.dirname(__file__)):
            local('python setup.py sdist')

def wheel():
    with virtualenv(VENV_DIR) as venv_local:
        with lcd(path.dirname(__file__)):
            venv_local('python setup.py bdist_wheel')


def clean():
    with lcd(path.dirname(__file__)):
        with virtualenv(VENV_DIR) as venv_local:
            local('python setup.py clean --all')


def test():
    with virtualenv(VENV_DIR) as venv_local:
        with lcd(path.dirname(__file__)):
            venv_local('pytest -x spacy/tests')
