import json

from fabric.api import local, run, lcd, cd, env

def make():
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

