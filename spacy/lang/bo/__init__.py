from ...language import BaseDefaults, Language
from .lex_attrs import LEX_ATTRS
from .stop_words import STOP_WORDS


class TibetanDefaults(BaseDefaults):
    lex_attr_getters = LEX_ATTRS
    stop_words = STOP_WORDS


class Tibetan(Language):
    lang = "bo"
    Defaults = TibetanDefaults


__all__ = ["Tibetan"]
