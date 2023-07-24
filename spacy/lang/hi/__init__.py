from ...language import BaseDefaults, Language
from .lex_attrs import LEX_ATTRS
from .stop_words import STOP_WORDS


class HindiDefaults(BaseDefaults):
    stop_words = STOP_WORDS
    lex_attr_getters = LEX_ATTRS


class Hindi(Language):
    lang = "hi"
    Defaults = HindiDefaults


__all__ = ["Hindi"]
