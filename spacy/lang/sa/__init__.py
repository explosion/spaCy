from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from ...language import Language


class SanskritDefaults(Language.Defaults):  # type: ignore[misc, valid-type]
    lex_attr_getters = LEX_ATTRS
    stop_words = STOP_WORDS


class Sanskrit(Language):
    lang = "sa"
    Defaults = SanskritDefaults


__all__ = ["Sanskrit"]
