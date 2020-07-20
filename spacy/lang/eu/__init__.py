from typing import Set, Dict, Callable, Any
from thinc.api import Config

from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .punctuation import TOKENIZER_SUFFIXES
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...language import Language
from ...util import registry


DEFAULT_CONFIG = """
[nlp]
lang = "eu"
stop_words = {"@language_data": "spacy.eu.stop_words"}
lex_attr_getters = {"@language_data": "spacy.eu.lex_attr_getters"}
"""


@registry.language_data("spacy.eu.stop_words")
def stop_words() -> Set[str]:
    return STOP_WORDS


@registry.language_data("spacy.eu.lex_attr_getters")
def lex_attr_getters() -> Dict[int, Callable[[str], Any]]:
    return LEX_ATTRS


class BasqueDefaults(Language.Defaults):
    tokenizer_exceptions = BASE_EXCEPTIONS
    suffixes = TOKENIZER_SUFFIXES


class Basque(Language):
    lang = "eu"
    Defaults = BasqueDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Basque"]
