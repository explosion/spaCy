#!/usr/bin/env python
""" cythonize.py

Cythonize pyx files into C++ files as needed.

Usage: cythonize.py [root]

Checks pyx files to see if they have been changed relative to their
corresponding C++ files. If they have, then runs cython on these files to
recreate the C++ files.

Additionally, checks pxd files and setup.py if they have been changed. If
they have, rebuilds everything.

Change detection based on file hashes stored in JSON format.

For now, this script should be run by developers when changing Cython files
and the resulting C++ files checked in, so that end-users (and Python-only
developers) do not get the Cython dependencies.

Based upon:

https://raw.github.com/dagss/private-scipy-refactor/cythonize/cythonize.py
https://raw.githubusercontent.com/numpy/numpy/master/tools/cythonize.py

Note: this script does not check any of the dependent C++ libraries.
"""
from __future__ import print_function

import os
import sys
import json
import hashlib
import subprocess
import argparse


HASH_FILE = "cythonize.json"


def process_pyx(fromfile, tofile, language_level="-2"):
    print("Processing %s" % fromfile)
    try:
        from Cython.Compiler.Version import version as cython_version
        from distutils.version import LooseVersion

        if LooseVersion(cython_version) < LooseVersion("0.19"):
            raise Exception("Require Cython >= 0.19")

    except ImportError:
        pass

    flags = ["--fast-fail", language_level]
    if tofile.endswith(".cpp"):
        flags += ["--cplus"]

    try:
        try:
            r = subprocess.call(
                ["cython"] + flags + ["-o", tofile, fromfile], env=os.environ
            )  # See Issue #791
            if r != 0:
                raise Exception("Cython failed")
        except OSError:
            # There are ways of installing Cython that don't result in a cython
            # executable on the path, see gh-2397.
            r = subprocess.call(
                [
                    sys.executable,
                    "-c",
                    "import sys; from Cython.Compiler.Main import "
                    "setuptools_main as main; sys.exit(main())",
                ]
                + flags
                + ["-o", tofile, fromfile]
            )
            if r != 0:
                raise Exception("Cython failed")
    except OSError:
        raise OSError("Cython needs to be installed")


def preserve_cwd(path, func, *args):
    orig_cwd = os.getcwd()
    try:
        os.chdir(path)
        func(*args)
    finally:
        os.chdir(orig_cwd)


def load_hashes(filename):
    try:
        return json.load(open(filename))
    except (ValueError, IOError):
        return {}


def save_hashes(hash_db, filename):
    with open(filename, "w") as f:
        f.write(json.dumps(hash_db))


def get_hash(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def hash_changed(base, path, db):
    full_path = os.path.normpath(os.path.join(base, path))
    return not get_hash(full_path) == db.get(full_path)


def hash_add(base, path, db):
    full_path = os.path.normpath(os.path.join(base, path))
    db[full_path] = get_hash(full_path)


def process(base, filename, db):
    root, ext = os.path.splitext(filename)
    if ext in [".pyx", ".cpp"]:
        if hash_changed(base, filename, db) or not os.path.isfile(
            os.path.join(base, root + ".cpp")
        ):
            preserve_cwd(base, process_pyx, root + ".pyx", root + ".cpp")
            hash_add(base, root + ".cpp", db)
            hash_add(base, root + ".pyx", db)


def check_changes(root, db):
    res = False
    new_db = {}

    setup_filename = "setup.py"
    hash_add(".", setup_filename, new_db)
    if hash_changed(".", setup_filename, db):
        res = True

    for base, _, files in os.walk(root):
        for filename in files:
            if filename.endswith(".pxd"):
                hash_add(base, filename, new_db)
                if hash_changed(base, filename, db):
                    res = True

    if res:
        db.clear()
        db.update(new_db)
    return res


def run(root):
    db = load_hashes(HASH_FILE)

    try:
        check_changes(root, db)
        for base, _, files in os.walk(root):
            for filename in files:
                process(base, filename, db)
    finally:
        save_hashes(db, HASH_FILE)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Cythonize pyx files into C++ files as needed"
    )
    parser.add_argument("root", help="root directory")
    args = parser.parse_args()
    run(args.root)
