from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from ...language import Language


class ArmenianDefaults(Language.Defaults):
    lex_attr_getters = LEX_ATTRS
    stop_words = STOP_WORDS


class Armenian(Language):
    lang = "hy"
    Defaults = ArmenianDefaults


__all__ = ["Armenian"]
