# coding: utf-8
from __future__ import unicode_literals, print_function

from fabric.api import local, lcd, env, settings, prefix
from fabtools.python import virtualenv
from os import path, environ


PWD = path.dirname(__file__)
ENV = environ['VENV_DIR'] if 'VENV_DIR' in environ else '.env'
VENV_DIR = path.join(PWD, ENV)


def env(lang='python2.7'):
    if path.exists(VENV_DIR):
        local('rm -rf {env}'.format(env=VENV_DIR))
    local('virtualenv -p {lang} {env}'.format(lang=lang, env=VENV_DIR))


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
