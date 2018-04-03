# coding: utf8
from __future__ import unicode_literals

from .errors import Errors, Warnings, deprecation_warning

try:
    # check if spaCy has compiled correctly (if it hasn't this will raise)
    import spacy.symbols
except ModuleNotFoundError:
    raise ImportError(Errors.E094)

from .cli.info import info as cli_info
from .glossary import explain
from .about import __version__
from . import util


def load(name, **overrides):
    depr_path = overrides.get('path')
    if depr_path not in (True, False, None):
        deprecation_warning(Warnings.W001.format(path=depr_path))
    return util.load_model(name, **overrides)


def blank(name, **kwargs):
    LangClass = util.get_lang_class(name)
    return LangClass(**kwargs)


def info(model=None, markdown=False):
    return cli_info(model, markdown)
