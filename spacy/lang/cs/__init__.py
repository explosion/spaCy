from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from ...language import Language


class CzechDefaults(Language.Defaults):
    stop_words = STOP_WORDS
    lex_attr_getters = LEX_ATTRS


class Czech(Language):
    lang = "cs"
    Defaults = CzechDefaults


__all__ = ["Czech"]
