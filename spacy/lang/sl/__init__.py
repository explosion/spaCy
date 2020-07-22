from typing import Set
from thinc.api import Config

from .stop_words import STOP_WORDS
from ...language import Language
from ...util import registry


DEFAULT_CONFIG = """
[nlp]
lang = "sl"
stop_words = {"@language_data": "spacy.sl.stop_words"}
"""


@registry.language_data("spacy.sl.stop_words")
def stop_words() -> Set[str]:
    return STOP_WORDS


class Slovenian(Language):
    lang = "sl"
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Slovenian"]
