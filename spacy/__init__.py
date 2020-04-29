# coding: utf8
from __future__ import unicode_literals
import warnings
import sys

warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")

# These are imported as part of the API
from thinc.neural.util import prefer_gpu, require_gpu

from . import pipeline
from .cli.info import info as cli_info
from .glossary import explain
from .about import __version__
from .errors import Errors, Warnings
from . import util
from .util import registry
from .language import component


if sys.maxunicode == 65535:
    raise SystemError(Errors.E130)


def load(name, **overrides):
    depr_path = overrides.get("path")
    if depr_path not in (True, False, None):
        warnings.warn(Warnings.W001.format(path=depr_path), DeprecationWarning)
    return util.load_model(name, **overrides)


def blank(name, **kwargs):
    LangClass = util.get_lang_class(name)
    return LangClass(**kwargs)


def info(model=None, markdown=False, silent=False):
    return cli_info(model, markdown, silent)
