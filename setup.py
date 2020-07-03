#!/usr/bin/env python
from __future__ import print_function
import io
import os
import subprocess
import sys
import contextlib
from distutils.command.build_ext import build_ext
from distutils.sysconfig import get_python_inc
import distutils.util
from distutils import ccompiler, msvccompiler
from setuptools import Extension, setup, find_packages


def is_new_osx():
    """Check whether we're on OSX >= 10.10"""
    name = distutils.util.get_platform()
    if sys.platform != "darwin":
        return False
    elif name.startswith("macosx-10"):
        minor_version = int(name.split("-")[1].split(".")[1])
        if minor_version >= 7:
            return True
        else:
            return False
    else:
        return False


PACKAGES = find_packages()


MOD_NAMES = [
    "spacy.parts_of_speech",
    "spacy.strings",
    "spacy.lexeme",
    "spacy.vocab",
    "spacy.attrs",
    "spacy.kb",
    "spacy.morphology",
    "spacy.pipeline.pipes",
    "spacy.pipeline.morphologizer",
    "spacy.syntax.stateclass",
    "spacy.syntax._state",
    "spacy.tokenizer",
    "spacy.syntax.nn_parser",
    "spacy.syntax._parser_model",
    "spacy.syntax._beam_utils",
    "spacy.syntax.nonproj",
    "spacy.syntax.transition_system",
    "spacy.syntax.arc_eager",
    "spacy.gold",
    "spacy.tokens.doc",
    "spacy.tokens.span",
    "spacy.tokens.token",
    "spacy.tokens.morphanalysis",
    "spacy.tokens._retokenize",
    "spacy.matcher.matcher",
    "spacy.matcher.phrasematcher",
    "spacy.matcher.dependencymatcher",
    "spacy.syntax.ner",
    "spacy.symbols",
    "spacy.vectors",
]


COMPILE_OPTIONS = {
    "msvc": ["/Ox", "/EHsc"],
    "mingw32": ["-O2", "-Wno-strict-prototypes", "-Wno-unused-function"],
    "other": ["-O2", "-Wno-strict-prototypes", "-Wno-unused-function"],
}


LINK_OPTIONS = {"msvc": [], "mingw32": [], "other": []}


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


def generate_cython(root, source):
    print("Cythonizing sources")
    p = subprocess.call(
        [sys.executable, os.path.join(root, "bin", "cythonize.py"), source],
        env=os.environ,
    )
    if p != 0:
        raise RuntimeError("Running cythonize failed")


def is_source_release(path):
    return os.path.exists(os.path.join(path, "PKG-INFO"))


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
    if os.path.exists(".git"):
        try:
            out = _minimal_ext_cmd(["git", "rev-parse", "--short", "HEAD"])
            git_version = out.strip().decode("ascii")
        except:
            pass
    elif os.path.exists(filename):
        # must be a source distribution, use existing version file
        try:
            a = open(filename, "r")
            lines = a.readlines()
            git_version = lines[-1].split('"')[1]
        except:
            pass
        finally:
            a.close()

    text = """# THIS FILE IS GENERATED FROM SPACY SETUP.PY
#
GIT_VERSION = "%(git_version)s"
"""
    a = open(filename, "w")
    try:
        a.write(
            text % {"git_version": git_version,}
        )
    finally:
        a.close()


def clean(path):
    for name in MOD_NAMES:
        name = name.replace(".", "/")
        for ext in [".so", ".html", ".cpp", ".c"]:
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
    write_git_info_py()

    root = os.path.abspath(os.path.dirname(__file__))

    if len(sys.argv) > 1 and sys.argv[1] == "clean":
        return clean(root)

    with chdir(root):
        with io.open(os.path.join(root, "spacy", "about.py"), encoding="utf8") as f:
            about = {}
            exec(f.read(), about)

        include_dirs = [
            get_python_inc(plat_specific=True),
            os.path.join(root, "include"),
        ]

        if (
            ccompiler.new_compiler().compiler_type == "msvc"
            and msvccompiler.get_build_version() == 9
        ):
            include_dirs.append(os.path.join(root, "include", "msvc9"))

        ext_modules = []
        for mod_name in MOD_NAMES:
            mod_path = mod_name.replace(".", "/") + ".cpp"
            extra_link_args = []
            # ???
            # Imported from patch from @mikepb
            # See Issue #267. Running blind here...
            if sys.platform == "darwin":
                dylib_path = [".." for _ in range(mod_name.count("."))]
                dylib_path = "/".join(dylib_path)
                dylib_path = "@loader_path/%s/spacy/platform/darwin/lib" % dylib_path
                extra_link_args.append("-Wl,-rpath,%s" % dylib_path)
            ext_modules.append(
                Extension(
                    mod_name,
                    [mod_path],
                    language="c++",
                    include_dirs=include_dirs,
                    extra_link_args=extra_link_args,
                )
            )

        if not is_source_release(root):
            generate_cython(root, "spacy")

        setup(
            name="spacy",
            packages=PACKAGES,
            version=about["__version__"],
            ext_modules=ext_modules,
            cmdclass={"build_ext": build_ext_subclass},
        )


if __name__ == "__main__":
    setup_package()
