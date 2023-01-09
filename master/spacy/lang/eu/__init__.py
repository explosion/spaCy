from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .punctuation import TOKENIZER_SUFFIXES
from ...language import Language, BaseDefaults


class BasqueDefaults(BaseDefaults):
    suffixes = TOKENIZER_SUFFIXES
    stop_words = STOP_WORDS
    lex_attr_getters = LEX_ATTRS


class Basque(Language):
    lang = "eu"
    Defaults = BasqueDefaults


__all__ = ["Basque"]
