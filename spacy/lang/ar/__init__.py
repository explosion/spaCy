from typing import Set, Dict, Callable, Any
from thinc.api import Config

from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .punctuation import TOKENIZER_SUFFIXES
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from ...language import Language
from ...util import registry


DEFAULT_CONFIG = """
[nlp]
lang = "ar"
stop_words = {"@language_data": "spacy.ar.stop_words"}
lex_attr_getters = {"@language_data": "spacy.ar.lex_attr_getters"}

[nlp.writing_system]
direction = "rtl"
has_case = false
has_letters = true
"""


@registry.language_data("spacy.ar.stop_words")
def stop_words() -> Set[str]:
    return STOP_WORDS


@registry.language_data("spacy.ar.lex_attr_getters")
def lex_attr_getters() -> Dict[int, Callable[[str], Any]]:
    return LEX_ATTRS


class ArabicDefaults(Language.Defaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    suffixes = TOKENIZER_SUFFIXES


class Arabic(Language):
    lang = "ar"
    Defaults = ArabicDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Arabic"]
