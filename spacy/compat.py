# coding: utf8
from __future__ import unicode_literals

import six
import ftfy
import sys
import ujson

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


pickle = pickle
copy_reg = copy_reg
CudaStream = CudaStream
cupy = cupy
fix_text = ftfy.fix_text
copy_array = copy_array

is_python2 = six.PY2
is_python3 = six.PY3
is_windows = sys.platform.startswith('win')
is_linux = sys.platform.startswith('linux')
is_osx = sys.platform == 'darwin'


if is_python2:
    bytes_ = str
    unicode_ = unicode
    basestring_ = basestring
    input_ = raw_input
    json_dumps = lambda data: ujson.dumps(data, indent=2).decode('utf8')
    path2str = lambda path: str(path).decode('utf8')

elif is_python3:
    bytes_ = bytes
    unicode_ = str
    basestring_ = str
    input_ = input
    json_dumps = lambda data: ujson.dumps(data, indent=2)
    path2str = lambda path: str(path)

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
    return ((python2 == None or python2 == is_python2) and
            (python3 == None or python3 == is_python3) and
            (windows == None or windows == is_windows) and
            (linux == None or linux == is_linux) and
            (osx == None or osx == is_osx))


def normalize_string_keys(old):
    '''Given a dictionary, make sure keys are unicode strings, not bytes.'''
    new = {}
    for key, value in old.items():
        if isinstance(key, bytes_):
            new[key.decode('utf8')] = value
        else:
            new[key] = value
    return new


