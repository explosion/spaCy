from typing import Set, Dict, Callable, Any
from thinc.api import Config

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .lemmatizer import GreekLemmatizer
from .syntax_iterators import SYNTAX_ITERATORS
from .punctuation import TOKENIZER_PREFIXES, TOKENIZER_SUFFIXES, TOKENIZER_INFIXES
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...language import Language
from ...util import update_exc, registry


DEFAULT_CONFIG = """
[nlp]
lang = "el"
stop_words = {"@language_data": "spacy.el.stop_words"}
lex_attr_getters = {"@language_data": "spacy.el.lex_attr_getters"}

[nlp.lemmatizer]
@lemmatizers = "spacy.GreekLemmatizer.v1"

[nlp.lemmatizer.data_paths]
@language_data = "spacy-lookups-data"
lang = ${nlp:lang}
"""


@registry.lemmatizers("spacy.GreekLemmatizer.v1")
def create_greek_lemmatizer(data_paths: dict = {}) -> GreekLemmatizer:
    return GreekLemmatizer(data_paths=data_paths)


@registry.language_data("spacy.el.stop_words")
def stop_words() -> Set[str]:
    return STOP_WORDS


@registry.language_data("spacy.el.lex_attr_getters")
def lex_attr_getters() -> Dict[int, Callable[[str], Any]]:
    return LEX_ATTRS


class GreekDefaults(Language.Defaults):
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    prefixes = TOKENIZER_PREFIXES
    suffixes = TOKENIZER_SUFFIXES
    infixes = TOKENIZER_INFIXES
    syntax_iterators = SYNTAX_ITERATORS


class Greek(Language):
    lang = "el"
    Defaults = GreekDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Greek"]
