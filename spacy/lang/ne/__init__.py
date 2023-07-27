from ...language import BaseDefaults, Language
from .lex_attrs import LEX_ATTRS
from .stop_words import STOP_WORDS


class NepaliDefaults(BaseDefaults):
    stop_words = STOP_WORDS
    lex_attr_getters = LEX_ATTRS


class Nepali(Language):
    lang = "ne"
    Defaults = NepaliDefaults


__all__ = ["Nepali"]
