from typing import Set
from thinc.api import Config

from .stop_words import STOP_WORDS
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...language import Language
from ...util import update_exc, registry


DEFAULT_CONFIG = """
[nlp]
lang = "he"
stop_words = {"@language_data": "spacy.he.stop_words"}

[nlp.writing_system]
direction = "rtl"
has_case = false
has_letters = true
"""


@registry.language_data("spacy.he.stop_words")
def stop_words() -> Set[str]:
    return STOP_WORDS


class HebrewDefaults(Language.Defaults):
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS)


class Hebrew(Language):
    lang = "he"
    Defaults = HebrewDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Hebrew"]
