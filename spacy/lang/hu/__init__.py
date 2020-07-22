from typing import Set
from thinc.api import Config

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS, TOKEN_MATCH
from .punctuation import TOKENIZER_PREFIXES, TOKENIZER_SUFFIXES, TOKENIZER_INFIXES
from .stop_words import STOP_WORDS
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...language import Language
from ...util import update_exc, registry


DEFAULT_CONFIG = """
[nlp]
lang = "hu"
stop_words = {"@language_data": "spacy.hu.stop_words"}

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


class HungarianDefaults(Language.Defaults):
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    prefixes = TOKENIZER_PREFIXES
    suffixes = TOKENIZER_SUFFIXES
    infixes = TOKENIZER_INFIXES
    token_match = TOKEN_MATCH


class Hungarian(Language):
    lang = "hu"
    Defaults = HungarianDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Hungarian"]
