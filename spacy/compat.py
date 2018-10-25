# coding: utf8
from __future__ import unicode_literals

import sys
import ujson
import itertools
import locale

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
    from thinc.neural.optimizers import Optimizer
except ImportError:
    from thinc.neural.optimizers import Adam as Optimizer

pickle = pickle
copy_reg = copy_reg
CudaStream = CudaStream
cupy = cupy
copy_array = copy_array
izip = getattr(itertools, 'izip', zip)

is_windows = sys.platform.startswith('win')
is_linux = sys.platform.startswith('linux')
is_osx = sys.platform == 'darwin'

# See: https://github.com/benjaminp/six/blob/master/six.py
is_python2 = sys.version_info[0] == 2
is_python3 = sys.version_info[0] == 3
is_python_pre_3_5 = is_python2 or (is_python3 and sys.version_info[1] < 5)

if is_python2:
    bytes_ = str
    unicode_ = unicode  # noqa: F821
    basestring_ = basestring  # noqa: F821
    input_ = raw_input  # noqa: F821
    json_dumps = lambda data: ujson.dumps(data, indent=2, escape_forward_slashes=False).decode('utf8')
    path2str = lambda path: str(path).decode('utf8')

elif is_python3:
    bytes_ = bytes
    unicode_ = str
    basestring_ = str
    input_ = input
    json_dumps = lambda data: ujson.dumps(data, indent=2, escape_forward_slashes=False)
    path2str = lambda path: str(path)


def b_to_str(b_str):
    if is_python2:
        return b_str
    # important: if no encoding is set, string becomes "b'...'"
    return str(b_str, encoding='utf8')


def getattr_(obj, name, *default):
    if is_python3 and isinstance(name, bytes):
        name = name.decode('utf8')
    return getattr(obj, name, *default)


def symlink_to(orig, dest):
    if is_python2 and is_windows:
        import subprocess
        subprocess.call(['mklink', '/d', path2str(orig), path2str(dest)], shell=True)
    else:
        orig.symlink_to(dest)


def is_config(python2=None, python3=None, windows=None, linux=None, osx=None):
    return (python2 in (None, is_python2) and
            python3 in (None, is_python3) and
            windows in (None, is_windows) and
            linux in (None, is_linux) and
            osx in (None, is_osx))


def normalize_string_keys(old):
    """Given a dictionary, make sure keys are unicode strings, not bytes."""
    new = {}
    for key, value in old.items():
        if isinstance(key, bytes_):
            new[key.decode('utf8')] = value
        else:
            new[key] = value
    return new


def import_file(name, loc):
    loc = str(loc)
    if is_python_pre_3_5:
        import imp
        return imp.load_source(name, loc)
    else:
        import importlib.util
        spec = importlib.util.spec_from_file_location(name, str(loc))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


def locale_escape(string, errors='replace'):
    '''
    Mangle non-supported characters, for savages with ascii terminals.
    '''
    encoding = locale.getpreferredencoding()
    string = string.encode(encoding, errors).decode('utf8')
    return string
