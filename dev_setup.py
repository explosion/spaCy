#!/usr/bin/env python

import subprocess

# This is what we're down to...
try:
    import Cython
except ImportError:
    subprocess.call(['pip install cython'], shell=True)

try:
    import murmurhash
except ImportError:
    subprocess.call(['pip install murmurhash'], shell=True)

try:
    import cymem
except ImportError:
    subprocess.call(['pip install cymem'], shell=True)

try:
    import preshed
except ImportError:
    subprocess.call(['pip install preshed'], shell=True)

try:
    import thinc
except ImportError:
    subprocess.call(['pip install thinc'], shell=True)

try:
    import numpy
except ImportError:
    subprocess.call(['pip install numpy'], shell=True)


import Cython.Distutils
from Cython.Distutils import Extension
import distutils.core

import sys
import os
import os.path

from os import path
from glob import glob

import numpy


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

includes = ['.', numpy.get_include()]
cython_includes = ['.']


if 'VIRTUAL_ENV' in os.environ:
    includes += glob(path.join(os.environ['VIRTUAL_ENV'], 'include', 'site', '*'))
else:
    # If you're not using virtualenv, set your include dir here.
    pass

ext_args = {'language': "c++", "include_dirs": includes}

exts = [
    Extension("spacy.typedefs", ["spacy/typedefs.pyx"], **ext_args),
    Extension("spacy.strings", ["spacy/strings.pyx"], **ext_args),
    Extension("spacy.lexeme", ["spacy/lexeme.pyx"], **ext_args),
    Extension("spacy.vocab", ["spacy/vocab.pyx"], **ext_args),
    Extension("spacy.tokens", ["spacy/tokens.pyx"], **ext_args),
    Extension("spacy.morphology", ["spacy/morphology.pyx"], **ext_args),

    Extension("spacy._ml", ["spacy/_ml.pyx"], **ext_args),

    Extension("spacy.tokenizer", ["spacy/tokenizer.pyx"], **ext_args),
    Extension("spacy.en.attrs", ["spacy/en/attrs.pyx"], **ext_args),
    Extension("spacy.en.pos", ["spacy/en/pos.pyx"], **ext_args),
    Extension("spacy.syntax.parser", ["spacy/syntax/parser.pyx"], **ext_args),
    Extension("spacy.syntax._state", ["spacy/syntax/_state.pyx"], **ext_args),
    Extension("spacy.syntax.arc_eager", ["spacy/syntax/arc_eager.pyx"], **ext_args),
    Extension("spacy.syntax._parse_features", ["spacy/syntax/_parse_features.pyx"],
              **ext_args)
    
    #Extension("spacy.pos_feats", ["spacy/pos_feats.pyx"], language="c++", include_dirs=includes),
    #Extension("spacy.ner._state", ["spacy/ner/_state.pyx"], language="c++", include_dirs=includes),
    #Extension("spacy.ner.bilou_moves", ["spacy/ner/bilou_moves.pyx"], language="c++", include_dirs=includes),
    #Extension("spacy.ner.io_moves", ["spacy/ner/io_moves.pyx"], language="c++", include_dirs=includes),
    #Extension("spacy.ner.greedy_parser", ["spacy/ner/greedy_parser.pyx"], language="c++", include_dirs=includes),
    #Extension("spacy.ner.pystate", ["spacy/ner/pystate.pyx"], language="c++", include_dirs=includes),
    #Extension("spacy.ner.context", ["spacy/ner/context.pyx"], language="c++", include_dirs=includes),
    #Extension("spacy.ner.feats", ["spacy/ner/feats.pyx"], language="c++", include_dirs=includes),
    #Extension("spacy.ner.annot", ["spacy/ner/annot.pyx"], language="c++", include_dirs=includes),
]


if sys.argv[1] == 'clean':
    print >> sys.stderr, "cleaning .c, .c++ and .so files matching sources"
    map(clean, exts)

distutils.core.setup(
    name='spacy',
    packages=['spacy', 'spacy.en', 'spacy.syntax'],
    description="Industrial-strength NLP",
    author='Matthew Honnibal',
    author_email='honnibal@gmail.com',
    version='0.1',
    url="http://honnibal.github.io/spaCy/",
    package_data={"spacy": ["*.pxd"], "spacy.en": ["*.pxd", "data/pos/*",
                            "data/wordnet/*", "data/tokenizer/*",
                            "data/vocab/*"],
                  "spacy.syntax": ["*.pxd"]},
    cmdclass={'build_ext': Cython.Distutils.build_ext},
    ext_modules=exts,
    license="Dual: Commercial or AGPL",
    requires=['cython', 'murmurhash', 'cymem', 'preshed', 'thinc', "unidecode",
              "ujson"]
)
