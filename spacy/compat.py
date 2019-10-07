# coding: utf8
"""
Helpers for Python and platform compatibility. To distinguish them from
the builtin functions, replacement functions are suffixed with an underscore,
e.g. `unicode_`.

DOCS: https://spacy.io/api/top-level#compat
"""
from __future__ import unicode_literals

import os
import sys
import itertools
import ast

from thinc.neural.util import copy_array

try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    import copy_reg
except ImportError:
    import copyreg as copy_reg

try:
    from cupy.cuda.stream import Stream as CudaStream
except ImportError:
    CudaStream = None

try:
    import cupy
except ImportError:
    cupy = None

try:
    from thinc.neural.optimizers import Optimizer  # noqa: F401
except ImportError:
    from thinc.neural.optimizers import Adam as Optimizer  # noqa: F401

pickle = pickle
copy_reg = copy_reg
CudaStream = CudaStream
cupy = cupy
copy_array = copy_array
izip = getattr(itertools, "izip", zip)

is_windows = sys.platform.startswith("win")
is_linux = sys.platform.startswith("linux")
is_osx = sys.platform == "darwin"

# See: https://github.com/benjaminp/six/blob/master/six.py
is_python2 = sys.version_info[0] == 2
is_python3 = sys.version_info[0] == 3
is_python_pre_3_5 = is_python2 or (is_python3 and sys.version_info[1] < 5)

if is_python2:
    bytes_ = str
    unicode_ = unicode  # noqa: F821
    basestring_ = basestring  # noqa: F821
    input_ = raw_input  # noqa: F821
    path2str = lambda path: str(path).decode("utf8")

elif is_python3:
    bytes_ = bytes
    unicode_ = str
    basestring_ = str
    input_ = input
    path2str = lambda path: str(path)


def b_to_str(b_str):
    """Convert a bytes object to a string.

    b_str (bytes): The object to convert.
    RETURNS (unicode): The converted string.
    """
    if is_python2:
        return b_str
    # Important: if no encoding is set, string becomes "b'...'"
    return str(b_str, encoding="utf8")


def symlink_to(orig, dest):
    """Create a symlink. Used for model shortcut links.

    orig (unicode / Path): The origin path.
    dest (unicode / Path): The destination path of the symlink.
    """
    if is_windows:
        import subprocess

        subprocess.check_call(
            ["mklink", "/d", path2str(orig), path2str(dest)], shell=True
        )
    else:
        orig.symlink_to(dest)


def symlink_remove(link):
    """Remove a symlink. Used for model shortcut links.

    link (unicode / Path): The path to the symlink.
    """
    # https://stackoverflow.com/q/26554135/6400719
    if os.path.isdir(path2str(link)) and is_windows:
        # this should only be on Py2.7 and windows
        os.rmdir(path2str(link))
    else:
        os.unlink(path2str(link))


def is_config(python2=None, python3=None, windows=None, linux=None, osx=None):
    """Check if a specific configuration of Python version and operating system
    matches the user's setup. Mostly used to display targeted error messages.

    python2 (bool): spaCy is executed with Python 2.x.
    python3 (bool): spaCy is executed with Python 3.x.
    windows (bool): spaCy is executed on Windows.
    linux (bool): spaCy is executed on Linux.
    osx (bool): spaCy is executed on OS X or macOS.
    RETURNS (bool): Whether the configuration matches the user's platform.

    DOCS: https://spacy.io/api/top-level#compat.is_config
    """
    return (
        python2 in (None, is_python2)
        and python3 in (None, is_python3)
        and windows in (None, is_windows)
        and linux in (None, is_linux)
        and osx in (None, is_osx)
    )


def import_file(name, loc):
    """Import module from a file. Used to load models from a directory.

    name (unicode): Name of module to load.
    loc (unicode / Path): Path to the file.
    RETURNS: The loaded module.
    """
    loc = path2str(loc)
    if is_python_pre_3_5:
        import imp

        return imp.load_source(name, loc)
    else:
        import importlib.util

        spec = importlib.util.spec_from_file_location(name, str(loc))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


def unescape_unicode(string):
    """Python2.7's re module chokes when compiling patterns that have ranges
    between escaped unicode codepoints if the two codepoints are unrecognised
    in the unicode database. For instance:

        re.compile('[\\uAA77-\\uAA79]').findall("hello")

    Ends up matching every character (on Python 2). This problem doesn't occur
    if we're dealing with unicode literals.
    """
    if string is None:
        return string
    # We only want to unescape the unicode, so we first must protect the other
    # backslashes.
    string = string.replace("\\", "\\\\")
    # Now we remove that protection for the unicode.
    string = string.replace("\\\\u", "\\u")
    string = string.replace("\\\\U", "\\U")
    # Now we unescape by evaling the string with the AST. This can't execute
    # code -- it only does the representational level.
    return ast.literal_eval("u'''" + string + "'''")
