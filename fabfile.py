import json

from fabric.api import local, run, lcd, cd, env

def make():
    local('python setup.py build_ext --inplace > /dev/null 2> /tmp/err')

def vmake():
    local('python setup.py build_ext --inplace')



def clean():
    local('python setup.py clean --all')


def docs():
    local('sphinx-build -b html docs/ .')


def test():
    local('py.test -x')

def sbox():
    local('python sb_setup.py build_ext --inplace')

def sbclean():
    local('python sb_setup.py clean --all')


def pos():
    local('python tools/train.py pos ~/work_data/docparse/wsj02-21.conll data/en/pos')
    local('python tools/tag.py ~/work_data/docparse/wsj22.raw /tmp/tmp')
    local('python tools/eval_pos.py ~/work_data/docparse/wsj22.conll /tmp/tmp')


def ner():
    local('rm -rf data/en/ner')
    local('python tools/train.py ner ~/work_data/ner/muc7.train data/en/ner')
    local('python tools/tag.py ~/work_data/ner/muc7.raw /tmp/ner')
    local('python tools/eval_ner.py ~/work_data/ner/muc7.dev /tmp/ner')
