#!/usr/bin/env python
import sys
import os
from os import path
from glob import glob
import subprocess
import numpy


from setuptools import setup
from distutils.core import Extension
import shutil


def clean(ext):
    for src in ext.sources:
        if src.endswith('.c') or src.endswith('cpp'):
            so = src.rsplit('.', 1)[0] + '.so'
            html = src.rsplit('.', 1)[0] + '.html'
            if os.path.exists(so):
                os.unlink(so)
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
    Extension("spacy.typedefs", ["spacy/typedefs.cpp"], **ext_args),
    Extension("spacy.strings", ["spacy/strings.cpp"], **ext_args),
    Extension("spacy.lexeme", ["spacy/lexeme.cpp"], **ext_args),
    Extension("spacy.vocab", ["spacy/vocab.cpp"], **ext_args),
    Extension("spacy.tokens", ["spacy/tokens.cpp"], **ext_args),
    Extension("spacy.morphology", ["spacy/morphology.cpp"], **ext_args),

    Extension("spacy._ml", ["spacy/_ml.cpp"], **ext_args),

    Extension("spacy.tokenizer", ["spacy/tokenizer.cpp"], **ext_args),
    Extension("spacy.en.attrs", ["spacy/en/attrs.cpp"], **ext_args),
    Extension("spacy.en.pos", ["spacy/en/pos.cpp"], **ext_args),
    Extension("spacy.syntax.parser", ["spacy/syntax/parser.cpp"], **ext_args),
    Extension("spacy.syntax._state", ["spacy/syntax/_state.cpp"], **ext_args),
    Extension("spacy.syntax.arc_eager", ["spacy/syntax/arc_eager.cpp"], **ext_args),
    Extension("spacy.syntax._parse_features", ["spacy/syntax/_parse_features.cpp"],
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


setup(
    name='spacy',
    packages=['spacy', 'spacy.en', 'spacy.syntax'],
    description="Industrial-strength NLP",
    author='Matthew Honnibal',
    author_email='honnibal@gmail.com',
    version='0.1',
    url="http://honnibal.github.io/spaCy/",
    package_data={"spacy": ["*.pxd"],
                  "spacy.en": ["*.pxd", "data/pos/*",
                               "data/wordnet/*", "data/tokenizer/*",
                               "data/vocab/*"],
                  "spacy.syntax": ["*.pxd"]},
    ext_modules=exts,
    license="Dual: Commercial or AGPL",
    install_requires=['murmurhash', 'cymem', 'preshed', 'thinc', "unidecode",
                      "ujson"]
)
