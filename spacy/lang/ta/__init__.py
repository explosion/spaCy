from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from ...language import Language, BaseDefaults


class TamilDefaults(BaseDefaults):
    lex_attr_getters = LEX_ATTRS
    stop_words = STOP_WORDS


class Tamil(Language):
    lang = "ta"
    Defaults = TamilDefaults


__all__ = ["Tamil"]
