from typing import Set
from thinc.api import Config

from .stop_words import STOP_WORDS
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...language import Language
from ...util import update_exc, registry


DEFAULT_CONFIG = """
[nlp]
lang = "hr"
stop_words = {"@language_data": "spacy.hr.stop_words"}

[nlp.lemmatizer]
@lemmatizers = "spacy.Lemmatizer.v1"

[nlp.lemmatizer.data_paths]
@language_data = "spacy-lookups-data"
lang = ${nlp:lang}
"""


@registry.language_data("spacy.hr.stop_words")
def stop_words() -> Set[str]:
    return STOP_WORDS


class CroatianDefaults(Language.Defaults):
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS)


class Croatian(Language):
    lang = "hr"
    Defaults = CroatianDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Croatian"]
