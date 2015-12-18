#!/usr/bin/env python
from __future__ import print_function
import os
import sys
import shutil
from subprocess import call


def x(cmd):
    print('$ '+cmd)
    res = call(cmd, shell=True)
    if res != 0:
        sys.exit(res)


if len(sys.argv) < 2:
    print('usage: %s <install-mode> [<pip-date>]')
    sys.exit(1)


install_mode = sys.argv[1]
pip_date = len(sys.argv) > 2 and sys.argv[2]


x('pip install -U pip')
if pip_date:
    x('python pip-date.py %s pip setuptools wheel six' % pip_date)
x('pip install -r requirements.txt')

if install_mode == 'pip':
    for filename in os.listdir('dist'):
        os.unlink(os.path.join('dist', filename))
    x('python setup.py sdist')
    filenames = os.listdir('dist')
    assert len(filenames) == 1
    x('pip install dist/%s' % filenames[0])

elif install_mode == 'setup-install':
    x('python setup.py install')

elif install_mode == 'setup-develop':
    x('pip install -e .')

x('pip install pytest')
x('pip list')

if os.path.exists('tmp'):
    shutil.rmtree('tmp')
os.mkdir('tmp')

try:
    old = os.getcwd()
    os.chdir('tmp')

    x('python -m spacy.en.download')
    x('python -m pytest ../spacy/ --models --vectors --slow')

finally:
    os.chdir(old)
