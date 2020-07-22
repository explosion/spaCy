from typing import Set, Dict, Callable, Any
from thinc.config import Config

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .syntax_iterators import noun_chunks
from .punctuation import TOKENIZER_INFIXES, TOKENIZER_SUFFIXES
from ...language import Language
from ...util import registry


DEFAULT_CONFIG = """
[nlp]
lang = "es"
stop_words = {"@language_data": "spacy.es.stop_words"}
lex_attr_getters = {"@language_data": "spacy.es.lex_attr_getters"}
get_noun_chunks = {"@language_data": "spacy.es.get_noun_chunks"}

[nlp.lemmatizer]
@lemmatizers = "spacy.Lemmatizer.v1"

[nlp.lemmatizer.data]
@language_data = "spacy-lookups-data"
lang = ${nlp:lang}
tables = ["lemma_lookup"]

[nlp.vocab_data]
@language_data = "spacy-lookups-data"
lang = ${nlp:lang}
tables = ["lexeme_cluster", "lexeme_prob", "lexeme_settings"]
"""


@registry.language_data("spacy.es.get_noun_chunks")
def get_noun_chunks() -> Callable:
    return noun_chunks


@registry.language_data("spacy.es.stop_words")
def stop_words() -> Set[str]:
    return STOP_WORDS


@registry.language_data("spacy.es.lex_attr_getters")
def lex_attr_getters() -> Dict[int, Callable[[str], Any]]:
    return LEX_ATTRS


class SpanishDefaults(Language.Defaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    infixes = TOKENIZER_INFIXES
    suffixes = TOKENIZER_SUFFIXES


class Spanish(Language):
    lang = "es"
    Defaults = SpanishDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Spanish"]
