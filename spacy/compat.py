# coding: utf8
from __future__ import unicode_literals

import six
import ftfy
import sys
import ujson

try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    import copy_reg
except ImportError:
    import copyreg as copy_reg


is_python2 = six.PY2
is_python3 = six.PY3
is_windows = sys.platform.startswith('win')
is_linux = sys.platform.startswith('linux')
is_osx = sys.platform == 'darwin'

fix_text = ftfy.fix_text


if is_python2:
    bytes_ = str
    unicode_ = unicode
    basestring_ = basestring
    input_ = raw_input
    json_dumps = lambda data: ujson.dumps(data, indent=2).decode('utf8')

elif is_python3:
    bytes_ = bytes
    unicode_ = str
    basestring_ = str
    input_ = input
    json_dumps = lambda data: ujson.dumps(data, indent=2)


def symlink_to(orig, dest):
    if is_python2 and is_windows:
        import subprocess
        subprocess.call(['mklink', '/d', unicode(orig), unicode(dest)], shell=True)
    else:
        orig.symlink_to(dest)


def is_config(python2=None, python3=None, windows=None, linux=None, osx=None):
    return ((python2 == None or python2 == is_python2) and
            (python3 == None or python3 == is_python3) and
            (windows == None or windows == is_windows) and
            (linux == None or linux == is_linux) and
            (osx == None or osx == is_osx))
