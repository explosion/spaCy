from typing import Set
from thinc.api import Config

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...language import Language
from ...util import update_exc, registry


DEFAULT_CONFIG = """
[nlp]
lang = "ga"
stop_words = {"@language_data": "spacy.ga.stop_words"}
"""


@registry.language_data("spacy.ga.stop_words")
def stop_words() -> Set[str]:
    return STOP_WORDS


class IrishDefaults(Language.Defaults):
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)


class Irish(Language):
    lang = "ga"
    Defaults = IrishDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Irish"]
