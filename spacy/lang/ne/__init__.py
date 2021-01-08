from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from ...language import Language


class NepaliDefaults(Language.Defaults):
    stop_words = STOP_WORDS
    lex_attr_getters = LEX_ATTRS


class Nepali(Language):
    lang = "ne"
    Defaults = NepaliDefaults


__all__ = ["Nepali"]
