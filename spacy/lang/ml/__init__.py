from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from ...language import Language


class MalayalamDefaults(Language.Defaults):
    lex_attr_getters = LEX_ATTRS
    stop_words = STOP_WORDS


class Malayalam(Language):
    lang = "ml"
    Defaults = MalayalamDefaults


__all__ = ["Malayalam"]
