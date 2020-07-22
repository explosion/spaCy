from typing import Set, Dict, Callable, Any
from thinc.config import Config

from .stop_words import STOP_WORDS
from .punctuation import TOKENIZER_SUFFIXES, TOKENIZER_PREFIXES, TOKENIZER_INFIXES
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .lex_attrs import LEX_ATTRS
from .syntax_iterators import noun_chunks
from ...language import Language
from ...util import registry


DEFAULT_CONFIG = """
[nlp]
lang = "id"
stop_words = {"@language_data": "spacy.id.stop_words"}
lex_attr_getters = {"@language_data": "spacy.id.lex_attr_getters"}
get_noun_chunks = {"@language_data": "spacy.id.get_noun_chunks"}

[nlp.lemmatizer]
@lemmatizers = "spacy.Lemmatizer.v1"

[nlp.lemmatizer.data]
@language_data = "spacy-lookups-data"
lang = ${nlp:lang}
tables = ["lemma_lookup"]

[nlp.vocab_data]
@language_data = "spacy-lookups-data"
lang = ${nlp:lang}
tables = ["lexeme_norm"]
"""


@registry.language_data("spacy.id.stop_words")
def stop_words() -> Set[str]:
    return STOP_WORDS


@registry.language_data("spacy.id.lex_attr_getters")
def lex_attr_getters() -> Dict[int, Callable[[str], Any]]:
    return LEX_ATTRS


@registry.language_data("spacy.id.get_noun_chunks")
def get_noun_chunks() -> Callable:
    return noun_chunks


class IndonesianDefaults(Language.Defaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    prefixes = TOKENIZER_PREFIXES
    suffixes = TOKENIZER_SUFFIXES
    infixes = TOKENIZER_INFIXES


class Indonesian(Language):
    lang = "id"
    Defaults = IndonesianDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Indonesian"]
