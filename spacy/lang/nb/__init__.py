from typing import Set, Callable
from thinc.api import Config

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .punctuation import TOKENIZER_PREFIXES, TOKENIZER_INFIXES
from .punctuation import TOKENIZER_SUFFIXES
from .stop_words import STOP_WORDS
from .syntax_iterators import noun_chunks
from ...language import Language
from ...util import registry


DEFAULT_CONFIG = """
[nlp]
lang = "nb"
stop_words = {"@language_data": "spacy.nb.stop_words"}
get_noun_chunks = {"@language_data": "spacy.nb.get_noun_chunks"}

[nlp.lemmatizer]
@lemmatizers = "spacy.Lemmatizer.v1"

[nlp.lemmatizer.data]
@language_data = "spacy-lookups-data"
lang = ${nlp:lang}
tables = ["lemma_lookup", "lemma_rules", "lemma_exc"]
"""


@registry.language_data("spacy.nb.stop_words")
def stop_words() -> Set[str]:
    return STOP_WORDS


@registry.language_data("spacy.nb.get_noun_chunks")
def get_noun_chunks() -> Callable:
    return noun_chunks


class NorwegianDefaults(Language.Defaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    prefixes = TOKENIZER_PREFIXES
    infixes = TOKENIZER_INFIXES
    suffixes = TOKENIZER_SUFFIXES


class Norwegian(Language):
    lang = "nb"
    Defaults = NorwegianDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Norwegian"]
