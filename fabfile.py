from fabric.api import local, run, lcd, cd, env

def make():
    local('python setup.py build_ext --inplace')

def clean():
    local('python setup.py clean --all')

def test():
    local('py.test -x')
