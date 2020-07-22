from typing import Set, Dict, Callable, Any
from thinc.api import Config

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from ...util import registry
from ...language import Language
from .lemmatizer import UkrainianLemmatizer


DEFAULT_CONFIG = """
[nlp]
lang = "uk"
stop_words = {"@language_data": "spacy.uk.stop_words"}
lex_attr_getters = {"@language_data": "spacy.uk.lex_attr_getters"}

[nlp.lemmatizer]
@lemmatizers = "spacy.UkrainianLemmatizer.v1"
"""


@registry.language_data("spacy.uk.stop_words")
def stop_words() -> Set[str]:
    return STOP_WORDS


@registry.language_data("spacy.uk.lex_attr_getters")
def lex_attr_getters() -> Dict[int, Callable[[str], Any]]:
    return LEX_ATTRS


@registry.lemmatizers("spacy.UkrainianLemmatizer.v1")
def create_ukrainian_lemmatizer() -> UkrainianLemmatizer:
    return UkrainianLemmatizer()


class UkrainianDefaults(Language.Defaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS


class Ukrainian(Language):
    lang = "uk"
    Defaults = UkrainianDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Ukrainian"]
