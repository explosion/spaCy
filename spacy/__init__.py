# coding: utf8
from __future__ import unicode_literals

import importlib

from .compat import basestring_
from .cli.info import info
from .glossary import explain
from .deprecated import resolve_load_name
from . import util


def load(name, **overrides):
    name = resolve_load_name(name, **overrides)
    model_path = util.resolve_model_path(name)
    meta = util.parse_package_meta(model_path)
    if 'lang' not in meta:
        raise IOError('No language setting found in model meta.')
    cls = util.get_lang_class(meta['lang'])
    overrides['meta'] = meta
    overrides['path'] = model_path
    return cls(**overrides)
