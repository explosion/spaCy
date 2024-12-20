import sys
from pathlib import Path
from typing import Any, Dict, Iterable, Union

# set library-specific custom warning handling before doing anything else
from .errors import setup_default_warnings

setup_default_warnings()

# These are imported as part of the API
from thinc.api import Config, prefer_gpu, require_cpu, require_gpu

from . import pipeline, util
from .about import __version__
from .errors import Errors
from .glossary import explain
from .language import Language
from .util import logger, registry
from .vocab import Vocab

if sys.maxunicode == 65535:
    raise SystemError(Errors.E130)

__all__ = [
    "__version__",
    "blank",
    "Config",
    "Errors",
    "explain",
    "info",
    "Language",
    "load",
    "logger",
    "pipeline",
    "prefer_gpu",
    "registry",
    "require_cpu",
    "require_gpu",
    "util",
    "Vocab",
]


def load(
    name: Union[str, Path],
    *,
    vocab: Union[Vocab, bool] = True,
    disable: Union[str, Iterable[str]] = util._DEFAULT_EMPTY_PIPES,
    enable: Union[str, Iterable[str]] = util._DEFAULT_EMPTY_PIPES,
    exclude: Union[str, Iterable[str]] = util._DEFAULT_EMPTY_PIPES,
    config: Union[Dict[str, Any], Config] = util.SimpleFrozenDict(),
) -> Language:
    """Load a spaCy model from an installed package or a local path.

    name (str): Package name or model path.
    vocab (Vocab): A Vocab object. If True, a vocab is created.
    disable (Union[str, Iterable[str]]): Name(s) of pipeline component(s) to disable. Disabled
        pipes will be loaded but they won't be run unless you explicitly
        enable them by calling nlp.enable_pipe.
    enable (Union[str, Iterable[str]]): Name(s) of pipeline component(s) to enable. All other
        pipes will be disabled (but can be enabled later using nlp.enable_pipe).
    exclude (Union[str, Iterable[str]]): Name(s) of pipeline component(s) to exclude. Excluded
        components won't be loaded.
    config (Dict[str, Any] / Config): Config overrides as nested dict or dict
        keyed by section values in dot notation.
    RETURNS (Language): The loaded nlp object.
    """
    return util.load_model(
        name,
        vocab=vocab,
        disable=disable,
        enable=enable,
        exclude=exclude,
        config=config,
    )


def blank(
    name: str,
    *,
    vocab: Union[Vocab, bool] = True,
    config: Union[Dict[str, Any], Config] = util.SimpleFrozenDict(),
    meta: Dict[str, Any] = util.SimpleFrozenDict(),
) -> Language:
    """Create a blank nlp object for a given language code.

    name (str): The language code, e.g. "en".
    vocab (Vocab): A Vocab object. If True, a vocab is created.
    config (Dict[str, Any] / Config): Optional config overrides.
    meta (Dict[str, Any]): Overrides for nlp.meta.
    RETURNS (Language): The nlp object.
    """
    LangClass = util.get_lang_class(name)
    # We should accept both dot notation and nested dict here for consistency
    config = util.dot_to_dict(config)
    return LangClass.from_config(config, vocab=vocab, meta=meta)


def __getattr__(name):
    if name == "cli":
        import importlib

        return importlib.import_module("." + name, __name__)
    if name == "info":
        from .cli.info import info

        return info
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
