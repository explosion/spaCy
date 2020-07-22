from typing import Set
from thinc.api import Config

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .punctuation import TOKENIZER_PREFIXES, TOKENIZER_SUFFIXES, TOKENIZER_INFIXES
from .stop_words import STOP_WORDS
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...language import Language
from ...util import update_exc, registry


DEFAULT_CONFIG = """
[nlp]
lang = "bn"
stop_words = {"@language_data": "spacy.bn.stop_words"}

[nlp.lemmatizer]
@lemmatizers = "spacy.Lemmatizer.v1"

[nlp.lemmatizer.data]
@language_data = "spacy-lookups-data"
lang = ${nlp:lang}
tables = ["lemma_rules"]
"""


@registry.language_data("spacy.bn.stop_words")
def stop_words() -> Set[str]:
    return STOP_WORDS


class BengaliDefaults(Language.Defaults):
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    prefixes = TOKENIZER_PREFIXES
    suffixes = TOKENIZER_SUFFIXES
    infixes = TOKENIZER_INFIXES


class Bengali(Language):
    lang = "bn"
    Defaults = BengaliDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Bengali"]
