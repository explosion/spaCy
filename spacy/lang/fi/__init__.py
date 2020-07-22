from typing import Set, Dict, Callable, Any
from thinc.api import Config

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .punctuation import TOKENIZER_INFIXES, TOKENIZER_SUFFIXES
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...language import Language
from ...util import update_exc, registry


DEFAULT_CONFIG = """
[nlp]
lang = "fi"
stop_words = {"@language_data": "spacy.fi.stop_words"}
lex_attr_getters = {"@language_data": "spacy.fi.lex_attr_getters"}
"""


@registry.language_data("spacy.fi.stop_words")
def stop_words() -> Set[str]:
    return STOP_WORDS


@registry.language_data("spacy.fi.lex_attr_getters")
def lex_attr_getters() -> Dict[int, Callable[[str], Any]]:
    return LEX_ATTRS


class FinnishDefaults(Language.Defaults):
    infixes = TOKENIZER_INFIXES
    suffixes = TOKENIZER_SUFFIXES
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)


class Finnish(Language):
    lang = "fi"
    Defaults = FinnishDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Finnish"]
