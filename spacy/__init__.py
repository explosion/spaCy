# coding: utf8
from __future__ import unicode_literals
import warnings

# This is used to suppress numpy runtime warnings, which warn about irrelevant
# binary incompatibility. We could pin to a specific numpy version, but then
# we risk entering dependency hell if other packages pin to different constraints.
# Ideally we would somehow specify the warning to suppress?
with warnings.catch_warnings(record=True) as w:
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
