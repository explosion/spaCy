#!/usr/bin/env python
from __future__ import print_function
import io
import os
import subprocess
import sys
import contextlib
from distutils.command.build_ext import build_ext
from distutils.sysconfig import get_python_inc
from distutils import ccompiler, msvccompiler
from setuptools import Extension, setup, find_packages


PACKAGE_DATA = {'': ['*.pyx', '*.pxd', '*.txt', '*.tokens']}


PACKAGES = find_packages()


MOD_NAMES = [
    'spacy.parts_of_speech',
    'spacy.strings',
    'spacy.lexeme',
    'spacy.vocab',
    'spacy.attrs',
    'spacy.morphology',
    'spacy.pipeline',
    'spacy.syntax.stateclass',
    'spacy.syntax._state',
    'spacy.syntax._beam_utils',
    'spacy.tokenizer',
    'spacy.syntax.nn_parser',
    'spacy.syntax.nonproj',
    'spacy.syntax.transition_system',
    'spacy.syntax.arc_eager',
    'spacy.gold',
    'spacy.tokens.doc',
    'spacy.tokens.span',
    'spacy.tokens.token',
    'spacy.matcher',
    'spacy.syntax.ner',
    'spacy.symbols',
    'spacy.vectors',
]


COMPILE_OPTIONS =  {
    'msvc': ['/Ox', '/EHsc'],
    'mingw32' : ['-O3', '-Wno-strict-prototypes', '-Wno-unused-function'],
    'other' : ['-O3', '-Wno-strict-prototypes', '-Wno-unused-function',
               '-march=native']
}


LINK_OPTIONS = {
    'msvc' : [],
    'mingw32': [],
    'other' : []
}


# I don't understand this very well yet. See Issue #267
# Fingers crossed!
USE_OPENMP_DEFAULT = '0' if sys.platform != 'darwin' else None
if os.environ.get('USE_OPENMP', USE_OPENMP_DEFAULT) == '1':
    if sys.platform == 'darwin':
        COMPILE_OPTIONS['other'].append('-fopenmp')
        LINK_OPTIONS['other'].append('-fopenmp')
        PACKAGE_DATA['spacy.platform.darwin.lib'] = ['*.dylib']
        PACKAGES.append('spacy.platform.darwin.lib')

    elif sys.platform == 'win32':
        COMPILE_OPTIONS['msvc'].append('/openmp')

    else:
        COMPILE_OPTIONS['other'].append('-fopenmp')
        LINK_OPTIONS['other'].append('-fopenmp')


# By subclassing build_extensions we have the actual compiler that will be used which is really known only after finalize_options
# http://stackoverflow.com/questions/724664/python-distutils-how-to-get-a-compiler-that-is-going-to-be-used
class build_ext_options:
    def build_options(self):
        for e in self.extensions:
            e.extra_compile_args += COMPILE_OPTIONS.get(
                self.compiler.compiler_type, COMPILE_OPTIONS['other'])
        for e in self.extensions:
            e.extra_link_args += LINK_OPTIONS.get(
                self.compiler.compiler_type, LINK_OPTIONS['other'])


class build_ext_subclass(build_ext, build_ext_options):
    def build_extensions(self):
        build_ext_options.build_options(self)
        build_ext.build_extensions(self)


def generate_cython(root, source):
    print('Cythonizing sources')
    p = subprocess.call([sys.executable,
                         os.path.join(root, 'bin', 'cythonize.py'),
                         source], env=os.environ)
    if p != 0:
        raise RuntimeError('Running cythonize failed')


def is_source_release(path):
    return os.path.exists(os.path.join(path, 'PKG-INFO'))


def clean(path):
    for name in MOD_NAMES:
        name = name.replace('.', '/')
        for ext in ['.so', '.html', '.cpp', '.c']:
            file_path = os.path.join(path, name + ext)
            if os.path.exists(file_path):
                os.unlink(file_path)


@contextlib.contextmanager
def chdir(new_dir):
    old_dir = os.getcwd()
    try:
        os.chdir(new_dir)
        sys.path.insert(0, new_dir)
        yield
    finally:
        del sys.path[0]
        os.chdir(old_dir)


def setup_package():
    root = os.path.abspath(os.path.dirname(__file__))

    if len(sys.argv) > 1 and sys.argv[1] == 'clean':
        return clean(root)

    with chdir(root):
        with io.open(os.path.join(root, 'spacy', 'about.py'), encoding='utf8') as f:
            about = {}
            exec(f.read(), about)

        with io.open(os.path.join(root, 'README.rst'), encoding='utf8') as f:
            readme = f.read()

        include_dirs = [
            get_python_inc(plat_specific=True),
            os.path.join(root, 'include')]

        if (ccompiler.new_compiler().compiler_type == 'msvc'
        and msvccompiler.get_build_version() == 9):
            include_dirs.append(os.path.join(root, 'include', 'msvc9'))

        ext_modules = []
        for mod_name in MOD_NAMES:
            mod_path = mod_name.replace('.', '/') + '.cpp'
            extra_link_args = []
            # ???
            # Imported from patch from @mikepb
            # See Issue #267. Running blind here...
            if sys.platform == 'darwin':
                dylib_path = ['..' for _ in range(mod_name.count('.'))]
                dylib_path = '/'.join(dylib_path)
                dylib_path = '@loader_path/%s/spacy/platform/darwin/lib' % dylib_path
                extra_link_args.append('-Wl,-rpath,%s' % dylib_path)
            ext_modules.append(
                Extension(mod_name, [mod_path],
                    language='c++', include_dirs=include_dirs,
                    extra_link_args=extra_link_args))

        if not is_source_release(root):
            generate_cython(root, 'spacy')

        setup(
            name=about['__title__'],
            zip_safe=False,
            packages=PACKAGES,
            package_data=PACKAGE_DATA,
            description=about['__summary__'],
            long_description=readme,
            author=about['__author__'],
            author_email=about['__email__'],
            version=about['__version__'],
            url=about['__uri__'],
            license=about['__license__'],
            ext_modules=ext_modules,
            scripts=['bin/spacy'],
            install_requires=[
                'numpy>=1.7',
                'murmurhash>=0.28,<0.29',
                'cymem>=1.30,<1.32',
                'preshed>=1.0.0,<2.0.0',
                'thinc>=6.10.0,<6.11.0',
                'plac<1.0.0,>=0.9.6',
                'six',
                'pathlib',
                'ujson>=1.35',
                'dill>=0.2,<0.3',
                'requests>=2.13.0,<3.0.0',
                'regex==2017.4.5',
                'ftfy>=4.4.2,<5.0.0',
                'msgpack-python',
                'msgpack-numpy'],
            classifiers=[
                'Development Status :: 5 - Production/Stable',
                'Environment :: Console',
                'Intended Audience :: Developers',
                'Intended Audience :: Science/Research',
                'License :: OSI Approved :: MIT License',
                'Operating System :: POSIX :: Linux',
                'Operating System :: MacOS :: MacOS X',
                'Operating System :: Microsoft :: Windows',
                'Programming Language :: Cython',
                'Programming Language :: Python :: 2.6',
                'Programming Language :: Python :: 2.7',
                'Programming Language :: Python :: 3.3',
                'Programming Language :: Python :: 3.4',
                'Programming Language :: Python :: 3.5',
                'Programming Language :: Python :: 3.6',
                'Topic :: Scientific/Engineering'],
            cmdclass = {
                'build_ext': build_ext_subclass},
        )


if __name__ == '__main__':
    setup_package()
