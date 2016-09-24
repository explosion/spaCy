import os
import io
import json
import re
import os.path

import six
from .attrs import TAG, HEAD, DEP, ENT_IOB, ENT_TYPE


LANGUAGES = {}


def set_lang_class(name, cls):
    global LANGUAGES
    LANGUAGES[name] = cls


def get_lang_class(name):
    lang = re.split('[^a-zA-Z0-9]', name, 1)[0]
    if lang not in LANGUAGES:
        raise RuntimeError('Language not supported: %s' % lang)
    return LANGUAGES[lang]


def normalize_slice(length, start, stop, step=None):
    if not (step is None or step == 1):
        raise ValueError("Stepped slices not supported in Span objects."
                         "Try: list(tokens)[start:stop:step] instead.")
    if start is None:
       start = 0
    elif start < 0:
       start += length
    start = min(length, max(0, start))

    if stop is None:
       stop = length
    elif stop < 0:
       stop += length
    stop = min(length, max(start, stop))

    assert 0 <= start <= stop <= length
    return start, stop


def utf8open(loc, mode='r'):
    return io.open(loc, mode, encoding='utf8')
