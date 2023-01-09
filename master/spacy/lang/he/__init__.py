from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from ...language import Language, BaseDefaults


class HebrewDefaults(BaseDefaults):
    stop_words = STOP_WORDS
    lex_attr_getters = LEX_ATTRS
    writing_system = {"direction": "rtl", "has_case": False, "has_letters": True}


class Hebrew(Language):
    lang = "he"
    Defaults = HebrewDefaults


__all__ = ["Hebrew"]
