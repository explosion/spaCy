# coding: utf8
from __future__ import unicode_literals

from .cli.info import info as cli_info
from .glossary import explain
from .about import __version__
from . import util


def load(name, **overrides):
    depr_path = overrides.get('path')
    if depr_path not in (True, False, None):
        util.deprecated(
            "As of spaCy v2.0, the keyword argument `path=` is deprecated. "
            "You can now call spacy.load with the path as its first argument, "
            "and the model's meta.json will be used to determine the language "
            "to load. For example:\nnlp = spacy.load('{}')".format(depr_path),
            'error')
    return util.load_model(name, **overrides)


def blank(name, **kwargs):
    LangClass = util.get_lang_class(name)
    return LangClass(**kwargs)


def info(model=None, markdown=False):
    return cli_info(None, model, markdown)
