from typing import Set, Dict, Callable, Any
from thinc.api import Config

from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .punctuation import TOKENIZER_PREFIXES, TOKENIZER_INFIXES
from .punctuation import TOKENIZER_SUFFIXES
from .lemmatizer import DutchLemmatizer
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...language import Language
from ...util import update_exc, registry


DEFAULT_CONFIG = """
[nlp]
lang = "nl"
stop_words = {"@language_data": "spacy.nl.stop_words"}
lex_attr_getters = {"@language_data": "spacy.nl.lex_attr_getters"}

[nlp.lemmatizer]
@lemmatizers = "spacy.DutchLemmatizer.v1"

[nlp.lemmatizer.data_paths]
@language_data = "spacy-lookups-data"
lang = ${nlp:lang}
"""


@registry.language_data("spacy.nl.stop_words")
def stop_words() -> Set[str]:
    return STOP_WORDS


@registry.language_data("spacy.nl.lex_attr_getters")
def lex_attr_getters() -> Dict[int, Callable[[str], Any]]:
    return LEX_ATTRS


@registry.lemmatizers("spacy.DutchLemmatizer.v1")
def create_dutch_lemmatizer(data_paths: dict = {}) -> DutchLemmatizer:
    return DutchLemmatizer(data_paths=data_paths)


class DutchDefaults(Language.Defaults):
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    prefixes = TOKENIZER_PREFIXES
    infixes = TOKENIZER_INFIXES
    suffixes = TOKENIZER_SUFFIXES


class Dutch(Language):
    lang = "nl"
    Defaults = DutchDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Dutch"]
