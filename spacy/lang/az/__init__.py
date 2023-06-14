from ...language import BaseDefaults, Language
from .lex_attrs import LEX_ATTRS
from .stop_words import STOP_WORDS


class AzerbaijaniDefaults(BaseDefaults):
    lex_attr_getters = LEX_ATTRS
    stop_words = STOP_WORDS


class Azerbaijani(Language):
    lang = "az"
    Defaults = AzerbaijaniDefaults


__all__ = ["Azerbaijani"]
