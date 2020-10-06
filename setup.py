#!/usr/bin/env python
from setuptools import Extension, setup, find_packages
import sys
import platform
from distutils.command.build_ext import build_ext
from distutils.sysconfig import get_python_inc
import numpy
from pathlib import Path
import shutil
from Cython.Build import cythonize
from Cython.Compiler import Options
import os
import subprocess


ROOT = Path(__file__).parent
PACKAGE_ROOT = ROOT / "spacy"


# Preserve `__doc__` on functions and classes
# http://docs.cython.org/en/latest/src/userguide/source_files_and_compilation.html#compiler-options
Options.docstrings = True

PACKAGES = find_packages()
MOD_NAMES = [
    "spacy.training.example",
    "spacy.parts_of_speech",
    "spacy.strings",
    "spacy.lexeme",
    "spacy.vocab",
    "spacy.attrs",
    "spacy.kb",
    "spacy.ml.parser_model",
    "spacy.morphology",
    "spacy.pipeline.dep_parser",
    "spacy.pipeline.morphologizer",
    "spacy.pipeline.multitask",
    "spacy.pipeline.ner",
    "spacy.pipeline.pipe",
    "spacy.pipeline.trainable_pipe",
    "spacy.pipeline.sentencizer",
    "spacy.pipeline.senter",
    "spacy.pipeline.tagger",
    "spacy.pipeline.transition_parser",
    "spacy.pipeline._parser_internals.arc_eager",
    "spacy.pipeline._parser_internals.ner",
    "spacy.pipeline._parser_internals.nonproj",
    "spacy.pipeline._parser_internals._state",
    "spacy.pipeline._parser_internals.stateclass",
    "spacy.pipeline._parser_internals.transition_system",
    "spacy.tokenizer",
    "spacy.training.gold_io",
    "spacy.tokens.doc",
    "spacy.tokens.span",
    "spacy.tokens.token",
    "spacy.tokens.morphanalysis",
    "spacy.tokens._retokenize",
    "spacy.matcher.matcher",
    "spacy.matcher.phrasematcher",
    "spacy.matcher.dependencymatcher",
    "spacy.symbols",
    "spacy.vectors",
]
COMPILE_OPTIONS = {
    "msvc": ["/Ox", "/EHsc"],
    "mingw32": ["-O2", "-Wno-strict-prototypes", "-Wno-unused-function"],
    "other": ["-O2", "-Wno-strict-prototypes", "-Wno-unused-function"],
}
LINK_OPTIONS = {"msvc": [], "mingw32": [], "other": []}
COMPILER_DIRECTIVES = {
    "language_level": -3,
    "embedsignature": True,
    "annotation_typing": False,
}
# Files to copy into the package that are otherwise not included
COPY_FILES = {
    ROOT / "setup.cfg": PACKAGE_ROOT / "tests" / "package",
    ROOT / "pyproject.toml": PACKAGE_ROOT / "tests" / "package",
    ROOT / "requirements.txt": PACKAGE_ROOT / "tests" / "package",
}


def is_new_osx():
    """Check whether we're on OSX >= 10.7"""
    if sys.platform != "darwin":
        return False
    mac_ver = platform.mac_ver()[0]
    if mac_ver.startswith("10"):
        minor_version = int(mac_ver.split(".")[1])
        if minor_version >= 7:
            return True
        else:
            return False
    return False


if is_new_osx():
    # On Mac, use libc++ because Apple deprecated use of
    # libstdc
    COMPILE_OPTIONS["other"].append("-stdlib=libc++")
    LINK_OPTIONS["other"].append("-lc++")
    # g++ (used by unix compiler on mac) links to libstdc++ as a default lib.
    # See: https://stackoverflow.com/questions/1653047/avoid-linking-to-libstdc
    LINK_OPTIONS["other"].append("-nodefaultlibs")


# By subclassing build_extensions we have the actual compiler that will be used which is really known only after finalize_options
# http://stackoverflow.com/questions/724664/python-distutils-how-to-get-a-compiler-that-is-going-to-be-used
class build_ext_options:
    def build_options(self):
        for e in self.extensions:
            e.extra_compile_args += COMPILE_OPTIONS.get(
                self.compiler.compiler_type, COMPILE_OPTIONS["other"]
            )
        for e in self.extensions:
            e.extra_link_args += LINK_OPTIONS.get(
                self.compiler.compiler_type, LINK_OPTIONS["other"]
            )


class build_ext_subclass(build_ext, build_ext_options):
    def build_extensions(self):
        build_ext_options.build_options(self)
        build_ext.build_extensions(self)


# Include the git version in the build (adapted from NumPy)
# Copyright (c) 2005-2020, NumPy Developers.
# BSD 3-Clause license, see licenses/3rd_party_licenses.txt
def write_git_info_py(filename="spacy/git_info.py"):
    def _minimal_ext_cmd(cmd):
        # construct minimal environment
        env = {}
        for k in ["SYSTEMROOT", "PATH", "HOME"]:
            v = os.environ.get(k)
            if v is not None:
                env[k] = v
        # LANGUAGE is used on win32
        env["LANGUAGE"] = "C"
        env["LANG"] = "C"
        env["LC_ALL"] = "C"
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, env=env)
        return out

    git_version = "Unknown"
    if Path(".git").exists():
        try:
            out = _minimal_ext_cmd(["git", "rev-parse", "--short", "HEAD"])
            git_version = out.strip().decode("ascii")
        except Exception:
            pass
    elif Path(filename).exists():
        # must be a source distribution, use existing version file
        try:
            a = open(filename, "r")
            lines = a.readlines()
            git_version = lines[-1].split('"')[1]
        except Exception:
            pass
        finally:
            a.close()

    text = """# THIS FILE IS GENERATED FROM SPACY SETUP.PY
#
GIT_VERSION = "%(git_version)s"
"""
    a = open(filename, "w")
    try:
        a.write(text % {"git_version": git_version})
    finally:
        a.close()


def clean(path):
    for path in path.glob("**/*"):
        if path.is_file() and path.suffix in (".so", ".cpp", ".html"):
            print(f"Deleting {path.name}")
            path.unlink()


def setup_package():
    write_git_info_py()
    if len(sys.argv) > 1 and sys.argv[1] == "clean":
        return clean(PACKAGE_ROOT)

    with (PACKAGE_ROOT / "about.py").open("r") as f:
        about = {}
        exec(f.read(), about)

    for copy_file, target_dir in COPY_FILES.items():
        if copy_file.exists():
            shutil.copy(str(copy_file), str(target_dir))
            print(f"Copied {copy_file} -> {target_dir}")

    include_dirs = [
        get_python_inc(plat_specific=True),
        numpy.get_include(),
    ]
    ext_modules = []
    for name in MOD_NAMES:
        mod_path = name.replace(".", "/") + ".pyx"
        ext = Extension(name, [mod_path], language="c++")
        ext_modules.append(ext)
    print("Cythonizing sources")
    ext_modules = cythonize(ext_modules, compiler_directives=COMPILER_DIRECTIVES)

    setup(
        name="spacy-nightly",
        packages=PACKAGES,
        version=about["__version__"],
        ext_modules=ext_modules,
        cmdclass={"build_ext": build_ext_subclass},
        include_dirs=include_dirs,
        package_data={"": ["*.pyx", "*.pxd", "*.pxi", "*.cpp"]},
    )


if __name__ == "__main__":
    setup_package()
