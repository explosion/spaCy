from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .punctuation import TOKENIZER_SUFFIXES
from ...language import Language


class UrduDefaults(Language.Defaults):
    suffixes = TOKENIZER_SUFFIXES
    lex_attr_getters = LEX_ATTRS
    stop_words = STOP_WORDS
    writing_system = {"direction": "rtl", "has_case": False, "has_letters": True}


class Urdu(Language):
    lang = "ur"
    Defaults = UrduDefaults


__all__ = ["Urdu"]
