# coding: utf8
from __future__ import unicode_literals

import importlib

from .compat import basestring_
from .cli.info import info
from .glossary import explain
from . import util


def load(name, **overrides):
    if overrides.get('path') not in (None, False, True):
        name = overrides.get('path')
    model_path = util.resolve_model_path(name)
    meta = util.parse_package_meta(model_path)
    if 'lang' not in meta:
        raise IOError('No language setting found in model meta.')
    module = importlib.import_module('.%s' % meta['lang'], 'spacy')
    cls = getattr(module, module.__all__[0])
    overrides['meta'] = meta
    overrides['path'] = model_path
    return cls(**overrides)
