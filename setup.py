#!/usr/bin/env python
from setuptools import setup
import shutil

import sys
import os
from os import path

from setuptools import Extension
from distutils import sysconfig
from distutils.core import setup, Extension
from distutils.command.build_ext import build_ext

import platform

PACKAGE_DATA =  {
    "spacy": ["*.pxd"],
    "spacy.tokens": ["*.pxd"],
    "spacy.serialize": ["*.pxd"],
    "spacy.syntax": ["*.pxd"],
    "spacy.en": [
        "*.pxd",
        "data/wordnet/*.exc",
        "data/wordnet/index.*",
        "data/tokenizer/*",
        "data/vocab/serializer.json"
    ]
}


# By subclassing build_extensions we have the actual compiler that will be used which is really known only after finalize_options
# http://stackoverflow.com/questions/724664/python-distutils-how-to-get-a-compiler-that-is-going-to-be-used
compile_options =  {'msvc'  : ['/Ox', '/EHsc']  ,
                    'other' : ['-O3', '-Wno-strict-prototypes', '-Wno-unused-function']       }
link_options    =  {'msvc'  : [] ,
                    'other' : [] }
class build_ext_options:
    def build_options(self):
        c_type = None
        if self.compiler.compiler_type in compile_options:
            c_type = self.compiler.compiler_type
        elif 'other' in compile_options:
            c_type = 'other'
        if c_type is not None:
           for e in self.extensions:
               e.extra_compile_args = compile_options[c_type]

        l_type = None 
        if self.compiler.compiler_type in link_options:
            l_type = self.compiler.compiler_type
        elif 'other' in link_options:
            l_type = 'other'
        if l_type is not None:
           for e in self.extensions:
               e.extra_link_args = link_options[l_type]

class build_ext_subclass( build_ext, build_ext_options ):
    def build_extensions(self):
        build_ext_options.build_options(self)
        build_ext.build_extensions(self)
        
    

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




def clean(mod_names):
    for name in mod_names:
        name = name.replace('.', '/')
        so = name + '.so'
        html = name + '.html'
        cpp = name + '.cpp'
        c = name + '.c'
        for file_path in [so, html, cpp, c]:
            if os.path.exists(file_path):
                os.unlink(file_path)


def name_to_path(mod_name, ext):
    return '%s.%s' % (mod_name.replace('.', '/'), ext)


def c_ext(mod_name, language, includes):
    mod_path = name_to_path(mod_name, language)
    return Extension(mod_name, [mod_path], include_dirs=includes)


def cython_setup(mod_names, language, includes):
    import Cython.Distutils
    import Cython.Build
    import distutils.core

    class build_ext_cython_subclass( Cython.Distutils.build_ext, build_ext_options ):
        def build_extensions(self):
            build_ext_options.build_options(self)
            Cython.Distutils.build_ext.build_extensions(self)

    if language == 'cpp':
        language = 'c++'
    exts = []
    for mod_name in mod_names:
        mod_path = mod_name.replace('.', '/') + '.pyx'
        e = Extension(mod_name, [mod_path], language=language, include_dirs=includes)
        exts.append(e)
    distutils.core.setup(
        name='spacy',
        packages=['spacy', 'spacy.tokens', 'spacy.en', 'spacy.serialize',
                  'spacy.syntax', 'spacy.munge'],
        description="Industrial-strength NLP",
        author='Matthew Honnibal',
        author_email='honnibal@gmail.com',
        version=VERSION,
        url="http://honnibal.github.io/spaCy/",
        package_data=PACKAGE_DATA,
        ext_modules=exts,
        cmdclass={'build_ext': build_ext_cython_subclass},
        license="MIT",
    )


def run_setup(exts):
    setup(
        name='spacy',
        packages=['spacy', 'spacy.tokens', 'spacy.en', 'spacy.serialize',
                  'spacy.syntax', 'spacy.munge',
                  'spacy.tests',
                  'spacy.tests.matcher',
                  'spacy.tests.morphology',
                  'spacy.tests.munge',
                  'spacy.tests.parser',
                  'spacy.tests.serialize',
                  'spacy.tests.span',
                  'spacy.tests.tagger',
                  'spacy.tests.tokenizer',
                  'spacy.tests.tokens',
                  'spacy.tests.vectors',
                  'spacy.tests.vocab'],
        description="Industrial-strength NLP",
        author='Matthew Honnibal',
        author_email='honnibal@gmail.com',
        version=VERSION,
        url="http://honnibal.github.io/spaCy/",
        package_data=PACKAGE_DATA,
        ext_modules=exts,
        license="MIT",
        install_requires=['numpy', 'murmurhash', 'cymem == 1.30', 'preshed == 0.43',
                          'thinc == 3.4.1', "text_unidecode", 'plac', 'six',
                          'ujson', 'cloudpickle'],
        setup_requires=["headers_workaround"],
        cmdclass = {'build_ext': build_ext_subclass },
    )

    import headers_workaround

    headers_workaround.fix_venv_pypy_include()
    headers_workaround.install_headers('murmurhash')
    headers_workaround.install_headers('numpy')


VERSION = '0.99'
def main(modules, is_pypy):
    language = "cpp"
    includes = ['.', path.join(sys.prefix, 'include')]
    if sys.platform.startswith('darwin'):
        compile_options['other'].append('-mmacosx-version-min=10.8')
        compile_options['other'].append('-stdlib=libc++')
        link_options['other'].append('-lc++')
    if use_cython:
        cython_setup(modules, language, includes)
    else:
        exts = [c_ext(mn, language, includes)
                      for mn in modules]
        run_setup(exts)

MOD_NAMES = ['spacy.parts_of_speech', 'spacy.strings',
             'spacy.lexeme', 'spacy.vocab', 'spacy.attrs',
             'spacy.morphology', 'spacy.tagger',
             'spacy.syntax.stateclass', 
             'spacy._ml', 'spacy._theano',
             'spacy.tokenizer',
             'spacy.syntax.parser', 
             'spacy.syntax.transition_system',
             'spacy.syntax.arc_eager',
             'spacy.syntax._parse_features',
             'spacy.gold', 'spacy.orth',
             'spacy.tokens.doc', 'spacy.tokens.span', 'spacy.tokens.token',
             'spacy.serialize.packer', 'spacy.serialize.huffman', 'spacy.serialize.bits',
             'spacy.cfile', 'spacy.matcher',
             'spacy.syntax.ner',
             'spacy.symbols']


if __name__ == '__main__':
    if sys.argv[1] == 'clean':
        clean(MOD_NAMES)
    else:
        use_cython = sys.argv[1] == 'build_ext'
        main(MOD_NAMES, use_cython)
