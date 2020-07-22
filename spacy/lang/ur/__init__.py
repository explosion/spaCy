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
lang = "ur"
stop_words = {"@language_data": "spacy.ur.stop_words"}
lex_attr_getters = {"@language_data": "spacy.ur.lex_attr_getters"}

[nlp.writing_system]
direction = "rtl"
has_case = false
has_letters = true

[nlp.lemmatizer]
@lemmatizers = "spacy.Lemmatizer.v1"

[nlp.lemmatizer.data]
@language_data = "spacy-lookups-data"
lang = ${nlp:lang}
tables = ["lemma_lookup"]
"""


@registry.language_data("spacy.ur.stop_words")
def stop_words() -> Set[str]:
    return STOP_WORDS


@registry.language_data("spacy.ur.lex_attr_getters")
def lex_attr_getters() -> Dict[int, Callable[[str], Any]]:
    return LEX_ATTRS


class UrduDefaults(Language.Defaults):
    tokenizer_exceptions = BASE_EXCEPTIONS
    suffixes = TOKENIZER_SUFFIXES


class Urdu(Language):
    lang = "ur"
    Defaults = UrduDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Urdu"]
