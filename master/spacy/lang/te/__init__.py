from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from ...language import Language, BaseDefaults


class TeluguDefaults(BaseDefaults):
    lex_attr_getters = LEX_ATTRS
    stop_words = STOP_WORDS


class Telugu(Language):
    lang = "te"
    Defaults = TeluguDefaults


__all__ = ["Telugu"]
