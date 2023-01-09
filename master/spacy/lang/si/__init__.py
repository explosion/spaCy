from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from ...language import Language, BaseDefaults


class SinhalaDefaults(BaseDefaults):
    lex_attr_getters = LEX_ATTRS
    stop_words = STOP_WORDS


class Sinhala(Language):
    lang = "si"
    Defaults = SinhalaDefaults


__all__ = ["Sinhala"]
