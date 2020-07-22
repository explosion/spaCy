from typing import Set, Dict, Callable, Any
from thinc.api import Config

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from ...language import Language
from ...util import registry
from .syntax_iterators import noun_chunks

# Punctuation stolen from Danish
from ..da.punctuation import TOKENIZER_INFIXES, TOKENIZER_SUFFIXES


DEFAULT_CONFIG = """
[nlp]
lang = "sv"
stop_words = {"@language_data": "spacy.sv.stop_words"}
lex_attr_getters = {"@language_data": "spacy.sv.lex_attr_getters"}
get_noun_chunks = {"@language_data": "spacy.sv.get_noun_chunks"}

[nlp.lemmatizer]
@lemmatizers = "spacy.Lemmatizer.v1"

[nlp.lemmatizer.data]
@language_data = "spacy-lookups-data"
lang = ${nlp:lang}
tables = ["lemma_lookup", "lemma_rules"]
"""


@registry.language_data("spacy.sv.stop_words")
def stop_words() -> Set[str]:
    return STOP_WORDS


@registry.language_data("spacy.sv.lex_attr_getters")
def lex_attr_getters() -> Dict[int, Callable[[str], Any]]:
    return LEX_ATTRS


@registry.language_data("spacy.sv.get_noun_chunks")
def get_noun_chunks() -> Callable:
    return noun_chunks


class SwedishDefaults(Language.Defaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    infixes = TOKENIZER_INFIXES
    suffixes = TOKENIZER_SUFFIXES


class Swedish(Language):
    lang = "sv"
    Defaults = SwedishDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Swedish"]
