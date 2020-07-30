from typing import Callable
from thinc.api import Config

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from ...util import registry
from ...language import Language
from .lemmatizer import UkrainianLemmatizer


DEFAULT_CONFIG = """
[nlp]

"""


@registry.lemmatizers("spacy.uk.UkrainianLemmatizer")
def create_ukrainian_lemmatizer() -> Callable[[Language], UkrainianLemmatizer]:
    def lemmatizer_factory(nlp: Language) -> UkrainianLemmatizer:
        return UkrainianLemmatizer()

    return lemmatizer_factory


class UkrainianDefaults(Language.Defaults):
    config = Config().from_str(DEFAULT_CONFIG)
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    lex_attr_getters = LEX_ATTRS
    stop_words = STOP_WORDS


class Ukrainian(Language):
    lang = "uk"
    Defaults = UkrainianDefaults


__all__ = ["Ukrainian"]
