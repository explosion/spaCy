from typing import Union, Iterable, Dict, Any
from pathlib import Path
import warnings
import sys

warnings.filterwarnings("ignore", message="numpy.dtype size changed")  # noqa
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")  # noqa

# These are imported as part of the API
from thinc.api import prefer_gpu, require_gpu  # noqa: F401
from thinc.api import Config

from . import pipeline  # noqa: F401
from .cli.info import info  # noqa: F401
from .glossary import explain  # noqa: F401
from .about import __version__  # noqa: F401
from .util import registry  # noqa: F401

from .errors import Errors
from .language import Language
from . import util

if sys.maxunicode == 65535:
    raise SystemError(Errors.E130)


def load(
    name: Union[str, Path],
    disable: Iterable[str] = tuple(),
    config: Union[Dict[str, Any], Config] = util.SimpleFrozenDict(),
) -> Language:
    """Load a spaCy model from an installed package or a local path.

    name (str): Package name or model path.
    disable (Iterable[str]): Names of pipeline components to disable.
    config (Dict[str, Any] / Config): Config overrides as nested dict or dict
        keyed by section values in dot notation.
    RETURNS (Language): The loaded nlp object.
    """
    return util.load_model(name, disable=disable, config=config)


def blank(name: str, **overrides) -> Language:
    """Create a blank nlp object for a given language code.

    name (str): The language code, e.g. "en".
    **overrides: Keyword arguments passed to language subclass on init.
    RETURNS (Language): The nlp object.
    """
    LangClass = util.get_lang_class(name)
    return LangClass(**overrides)
