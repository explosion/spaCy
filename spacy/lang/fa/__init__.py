from typing import Set, Dict, Callable, Any
from thinc.api import Config

from ...language import Language
from ...util import update_exc, registry
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .punctuation import TOKENIZER_SUFFIXES
from .syntax_iterators import SYNTAX_ITERATORS


DEFAULT_CONFIG = """
[nlp]
lang = "fa"
stop_words = {"@language_data": "spacy.fa.stop_words"}
lex_attr_getters = {"@language_data": "spacy.fa.lex_attr_getters"}

[nlp.writing_system]
direction = "rtl"
has_case = false
has_letters = true

[nlp.lemmatizer]
@lemmatizers = "spacy.Lemmatizer.v1"

[nlp.lemmatizer.data_paths]
@language_data = "spacy-lookups-data"
lang = ${nlp:lang}
"""


@registry.language_data("spacy.fa.stop_words")
def stop_words() -> Set[str]:
    return STOP_WORDS


@registry.language_data("spacy.fa.lex_attr_getters")
def lex_attr_getters() -> Dict[int, Callable[[str], Any]]:
    return LEX_ATTRS


class PersianDefaults(Language.Defaults):
    tokenizer_exceptions = update_exc(TOKENIZER_EXCEPTIONS)
    suffixes = TOKENIZER_SUFFIXES
    syntax_iterators = SYNTAX_ITERATORS


class Persian(Language):
    lang = "fa"
    Defaults = PersianDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Persian"]
