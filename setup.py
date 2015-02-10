#!/usr/bin/env python
import subprocess
from setuptools import setup
from glob import glob

import sys
import os
from os import path
from os.path import splitext


import shutil
from setuptools import Extension
from distutils import sysconfig
import platform

# PyPy --- NB! PyPy doesn't really work, it segfaults all over the place. But,
# this is necessary to get it compile.
# We have to resort to monkey-patching to set the compiler, because pypy broke
# all the everything.

pre_patch_customize_compiler = sysconfig.customize_compiler
def my_customize_compiler(compiler):
    pre_patch_customize_compiler(compiler)
    compiler.compiler_cxx = ['c++']


if platform.python_implementation() == 'PyPy':
    sysconfig.customize_compiler = my_customize_compiler


#def install_headers():
#    dest_dir = path.join(sys.prefix, 'include', 'murmurhash')
#    if not path.exists(dest_dir):
#        shutil.copytree('murmurhash/headers/murmurhash', dest_dir)
#
#    dest_dir = path.join(sys.prefix, 'include', 'numpy')


includes = ['.', path.join(sys.prefix, 'include')]


try:
    import numpy
    numpy_headers = path.join(numpy.get_include(), 'numpy')
    shutil.copytree(numpy_headers, path.join(sys.prefix, 'include', 'numpy'))
except ImportError:
    pass
except OSError:
    pass


def clean(ext):
    for src in ext.sources:
        if src.endswith('.c') or src.endswith('cpp'):
            so = src.rsplit('.', 1)[0] + '.so'
            html = src.rsplit('.', 1)[0] + '.html'
            if os.path.exists(so):
                os.unlink(so)
            if os.path.exists(html):
                os.unlink(html)


def name_to_path(mod_name, ext):
    return '%s.%s' % (mod_name.replace('.', '/'), ext)


def c_ext(mod_name, language, includes, compile_args):
    mod_path = name_to_path(mod_name, language)
    return Extension(mod_name, [mod_path], include_dirs=includes,
                     extra_compile_args=compile_args, extra_link_args=compile_args)


def cython_exts(mod_names, language, includes, compile_args):
    import Cython.Distutils
    import Cython.Build
    if language == 'cpp':
        language = 'c++'
    exts = []
    for mod_name in mod_names:
        mod_path = mod_name.replace('.', '/') + '.pyx'
        e = Extension(mod_name, [mod_path], language=language, include_dirs=includes,
                      extra_compile_args=compile_args)
        exts.append(e)
    return Cython.Build.cythonize(exts)


def run_setup(exts):
    setup(
        name='spacy',
        packages=['spacy', 'spacy.en', 'spacy.syntax'],
        description="Industrial-strength NLP",
        author='Matthew Honnibal',
        author_email='honnibal@gmail.com',
        version='0.61',
        url="http://honnibal.github.io/spaCy/",
        package_data={"spacy": ["*.pxd"],
                      "spacy.en": ["*.pxd", "data/pos/*",
                                   "data/wordnet/*", "data/tokenizer/*",
                                   "data/vocab/lexemes.bin",
                                   "data/vocab/strings.txt"],
                      "spacy.syntax": ["*.pxd"]},
        ext_modules=exts,
        license="Dual: Commercial or AGPL",
        install_requires=['numpy', 'murmurhash', 'cymem >= 1.11', 'preshed', 'thinc',
                          "unidecode", 'wget', 'plac', 'six'],
        setup_requires=["headers_workaround"],
    )

    import headers_workaround

    headers_workaround.fix_venv_pypy_include()
    headers_workaround.install_headers('murmurhash')
    headers_workaround.install_headers('numpy')


def main(modules, is_pypy):
    language = "cpp"
    includes = ['.', path.join(sys.prefix, 'include')]
    compile_args = ['-O3']
    if use_cython:
        exts = cython_exts(modules, language, includes, compile_args)
    else:
        exts = [c_ext(mn, language, includes, compile_args) for mn in modules]
    run_setup(exts)


MOD_NAMES = ['spacy.parts_of_speech', 'spacy.strings',
             'spacy.lexeme', 'spacy.vocab', 'spacy.tokens', 'spacy.morphology',
             'spacy._ml', 'spacy.tokenizer', 'spacy.en.attrs',
             'spacy.en.pos', 'spacy.syntax.parser', 'spacy.syntax._state',
             'spacy.syntax.arc_eager', 'spacy.syntax._parse_features',
             'spacy.orth']


if __name__ == '__main__':
    use_cython = sys.argv[1] == 'build_ext'
    main(MOD_NAMES, use_cython)
