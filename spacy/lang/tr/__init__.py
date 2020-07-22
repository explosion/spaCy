from typing import Set
from thinc.api import Config

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS
from ...language import Language
from ...util import registry


DEFAULT_CONFIG = """
[nlp]
lang = "tr"
stop_words = {"@language_data": "spacy.tr.stop_words"}

[nlp.lemmatizer]
@lemmatizers = "spacy.Lemmatizer.v1"

[nlp.lemmatizer.data]
@language_data = "spacy-lookups-data"
lang = ${nlp:lang}
tables = ["lemma_lookup"]
"""


@registry.language_data("spacy.tr.stop_words")
def stop_words() -> Set[str]:
    return STOP_WORDS


class TurkishDefaults(Language.Defaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS


class Turkish(Language):
    lang = "tr"
    Defaults = TurkishDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Turkish"]
