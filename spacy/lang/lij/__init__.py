from typing import Set
from thinc.api import Config

from .stop_words import STOP_WORDS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .punctuation import TOKENIZER_INFIXES
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...language import Language
from ...util import update_exc, registry


DEFAULT_CONFIG = """
[nlp]
lang = "lij"
stop_words = {"@language_data": "spacy.lij.stop_words"}
"""


@registry.language_data("spacy.lij.stop_words")
def stop_words() -> Set[str]:
    return STOP_WORDS


class LigurianDefaults(Language.Defaults):
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    infixes = TOKENIZER_INFIXES


class Ligurian(Language):
    lang = "lij"
    Defaults = LigurianDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Ligurian"]
