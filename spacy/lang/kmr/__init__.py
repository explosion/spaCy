from ...language import BaseDefaults, Language
from .lex_attrs import LEX_ATTRS
from .stop_words import STOP_WORDS


class KurmanjiDefaults(BaseDefaults):
    stop_words = STOP_WORDS
    lex_attr_getters = LEX_ATTRS


class Kurmanji(Language):
    lang = "kmr"
    Defaults = KurmanjiDefaults


__all__ = ["Kurmanji"]
