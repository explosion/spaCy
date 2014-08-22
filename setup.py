#!/usr/bin/env python
import Cython.Distutils
from Cython.Distutils import Extension
import distutils.core

import sys
import os
import os.path
from os import path
from glob import glob


def clean(ext):
    for pyx in ext.sources:
        if pyx.endswith('.pyx'):
            c = pyx[:-4] + '.c'
            cpp = pyx[:-4] + '.cpp'
            so = pyx[:-4] + '.so'
            html = pyx[:-4] + '.html'
            if os.path.exists(so):
                os.unlink(so)
            if os.path.exists(c):
                os.unlink(c)
            elif os.path.exists(cpp):
                os.unlink(cpp)
            if os.path.exists(html):
                os.unlink(html)


HERE = os.path.dirname(__file__)
virtual_env = os.environ.get('VIRTUAL_ENV', '')
compile_args = []
link_args = []
libs = []

includes = ['.']
cython_includes = ['.']


if 'VIRTUAL_ENV' in os.environ:
    includes += glob(path.join(os.environ['VIRTUAL_ENV'], 'include', 'site', '*'))
else:
    # If you're not using virtualenv, set your include dir here.
    pass


exts = [
    Extension("spacy.tokens", ["spacy/tokens.pyx"], language="c++", include_dirs=includes),
    Extension("spacy.en", ["spacy/en.pyx"], language="c++",
              include_dirs=includes),
    Extension("spacy.ptb3", ["spacy/ptb3.pyx"], language="c++", include_dirs=includes),
    Extension("spacy.lexeme", ["spacy/lexeme.pyx"], language="c++", include_dirs=includes),
    Extension("spacy.spacy", ["spacy/spacy.pyx"], language="c++", include_dirs=includes),
    Extension("spacy.string_tools", ["spacy/string_tools.pyx"], language="c++",
              include_dirs=includes),
    Extension("spacy.orthography.latin", ["spacy/orthography/latin.pyx"], language="c++",
              include_dirs=includes)
]


if sys.argv[1] == 'clean':
    print >> sys.stderr, "cleaning .c, .c++ and .so files matching sources"
    map(clean, exts)

distutils.core.setup(
    name='spaCy',
    packages=['spacy'],
    author='Matthew Honnibal',
    author_email='honnibal@gmail.com',
    version='1.0',
    cmdclass={'build_ext': Cython.Distutils.build_ext},
    ext_modules=exts,
)



