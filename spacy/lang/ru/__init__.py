from typing import Callable
from thinc.api import Config

from .stop_words import STOP_WORDS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .lex_attrs import LEX_ATTRS
from .lemmatizer import RussianLemmatizer
from ...util import registry
from ...language import Language


DEFAULT_CONFIG = """
[nlp]

"""


@registry.lemmatizers("spacy.ru.RussianLemmatizer")
def create_lemmatizer() -> Callable[[Language], RussianLemmatizer]:
    def lemmatizer_factory(nlp: Language) -> RussianLemmatizer:
        return RussianLemmatizer()

    return lemmatizer_factory


class RussianDefaults(Language.Defaults):
    config = Config().from_str(DEFAULT_CONFIG)
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    lex_attr_getters = LEX_ATTRS
    stop_words = STOP_WORDS


class Russian(Language):
    lang = "ru"
    Defaults = RussianDefaults


__all__ = ["Russian"]
