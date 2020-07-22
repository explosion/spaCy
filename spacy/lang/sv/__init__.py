from typing import Set, Dict, Callable, Any
from thinc.api import Config

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...language import Language
from ...util import update_exc, registry
from .syntax_iterators import SYNTAX_ITERATORS

# Punctuation stolen from Danish
from ..da.punctuation import TOKENIZER_INFIXES, TOKENIZER_SUFFIXES


DEFAULT_CONFIG = """
[nlp]
lang = "sv"
stop_words = {"@language_data": "spacy.sv.stop_words"}
lex_attr_getters = {"@language_data": "spacy.sv.lex_attr_getters"}

[nlp.lemmatizer]
@lemmatizers = "spacy.Lemmatizer.v1"

[nlp.lemmatizer.data_paths]
@language_data = "spacy-lookups-data"
lang = ${nlp:lang}
"""


@registry.language_data("spacy.sv.stop_words")
def stop_words() -> Set[str]:
    return STOP_WORDS


@registry.language_data("spacy.sv.lex_attr_getters")
def lex_attr_getters() -> Dict[int, Callable[[str], Any]]:
    return LEX_ATTRS


class SwedishDefaults(Language.Defaults):
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    infixes = TOKENIZER_INFIXES
    suffixes = TOKENIZER_SUFFIXES
    syntax_iterators = SYNTAX_ITERATORS


class Swedish(Language):
    lang = "sv"
    Defaults = SwedishDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Swedish"]
