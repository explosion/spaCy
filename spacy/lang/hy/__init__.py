from ...language import BaseDefaults, Language
from .lex_attrs import LEX_ATTRS
from .stop_words import STOP_WORDS


class ArmenianDefaults(BaseDefaults):
    lex_attr_getters = LEX_ATTRS
    stop_words = STOP_WORDS


class Armenian(Language):
    lang = "hy"
    Defaults = ArmenianDefaults


__all__ = ["Armenian"]
