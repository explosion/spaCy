from typing import Set
from thinc.api import Config

from .stop_words import STOP_WORDS
from ...language import Language
from ...util import registry


DEFAULT_CONFIG = """
[nlp]
lang = "af"
stop_words = {"@language_data": "spacy.af.stop_words"}
"""


@registry.language_data("spacy.af.stop_words")
def stop_words() -> Set[str]:
    return STOP_WORDS


class Afrikaans(Language):
    lang = "af"
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Afrikaans"]
