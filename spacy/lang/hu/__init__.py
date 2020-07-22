from typing import Set, Pattern
from thinc.api import Config

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS, TOKEN_MATCH
from .punctuation import TOKENIZER_PREFIXES, TOKENIZER_SUFFIXES, TOKENIZER_INFIXES
from .stop_words import STOP_WORDS
from ...language import Language
from ...util import registry


DEFAULT_CONFIG = """
[nlp]
lang = "hu"
stop_words = {"@language_data": "spacy.hu.stop_words"}

[nlp.tokenizer]
@tokenizers = "spacy.Tokenizer.v1"
token_match = {"@language_data": "spacy.hu.token_match"}

[nlp.lemmatizer]
@lemmatizers = "spacy.Lemmatizer.v1"

[nlp.lemmatizer.data]
@language_data = "spacy-lookups-data"
lang = ${nlp:lang}
tables = ["lemma_lookup"]
"""


@registry.language_data("spacy.hu.stop_words")
def stop_words() -> Set[str]:
    return STOP_WORDS


@registry.language_data("spacy.hu.token_match")
def token_match() -> Pattern:
    return TOKEN_MATCH


class HungarianDefaults(Language.Defaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    prefixes = TOKENIZER_PREFIXES
    suffixes = TOKENIZER_SUFFIXES
    infixes = TOKENIZER_INFIXES


class Hungarian(Language):
    lang = "hu"
    Defaults = HungarianDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Hungarian"]
