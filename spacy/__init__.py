# coding: utf8
from __future__ import unicode_literals

from .cli.info import info as cli_info
from .glossary import explain
from .about import __version__
from .errors import Warnings, deprecation_warning
from . import util


def load(name, **overrides):
    depr_path = overrides.get('path')
    if depr_path not in (True, False, None):
        deprecation_warning(Warnings.W001.format(path=depr_path))
    return util.load_model(name, **overrides)


def blank(name, **kwargs):
    LangClass = util.get_lang_class(name)
    return LangClass(**kwargs)


def info(model=None, markdown=False, silent=False):
    return cli_info(model, markdown, silent)
