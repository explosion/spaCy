from ...language import BaseDefaults, Language
from .lex_attrs import LEX_ATTRS
from .stop_words import STOP_WORDS


class MalayalamDefaults(BaseDefaults):
    lex_attr_getters = LEX_ATTRS
    stop_words = STOP_WORDS


class Malayalam(Language):
    lang = "ml"
    Defaults = MalayalamDefaults


__all__ = ["Malayalam"]
