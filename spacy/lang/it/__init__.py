from typing import Set
from thinc.api import Config

from .stop_words import STOP_WORDS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .punctuation import TOKENIZER_PREFIXES, TOKENIZER_INFIXES
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...language import Language
from ...util import update_exc, registry


DEFAULT_CONFIG = """
[nlp]
lang = "it"
stop_words = {"@language_data": "spacy.it.stop_words"}

[nlp.lemmatizer]
@lemmatizers = "spacy.Lemmatizer.v1"

[nlp.lemmatizer.data]
@language_data = "spacy-lookups-data"
lang = ${nlp:lang}
tables = ["lemma_lookup"]
"""


@registry.language_data("spacy.it.stop_words")
def stop_words() -> Set[str]:
    return STOP_WORDS


class ItalianDefaults(Language.Defaults):
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    stop_words = STOP_WORDS
    prefixes = TOKENIZER_PREFIXES
    infixes = TOKENIZER_INFIXES


class Italian(Language):
    lang = "it"
    Defaults = ItalianDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Italian"]
