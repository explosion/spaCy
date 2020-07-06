import warnings
import sys

warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")

# These are imported as part of the API
from thinc.api import prefer_gpu, require_gpu

from . import pipeline
from .cli.info import info
from .glossary import explain
from .about import __version__
from .errors import Errors, Warnings
from . import util
from .util import registry
from .language import component


if sys.maxunicode == 65535:
    raise SystemError(Errors.E130)


config = registry


def load(name, **overrides):
    return util.load_model(name, **overrides)


def blank(name, **kwargs):
    LangClass = util.get_lang_class(name)
    return LangClass(**kwargs)
