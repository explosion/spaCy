from ...language import BaseDefaults, Language
from .lex_attrs import LEX_ATTRS
from .punctuation import TOKENIZER_SUFFIXES
from .stop_words import STOP_WORDS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS


class ArabicDefaults(BaseDefaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    suffixes = TOKENIZER_SUFFIXES
    stop_words = STOP_WORDS
    lex_attr_getters = LEX_ATTRS
    writing_system = {"direction": "rtl", "has_case": False, "has_letters": True}


class Arabic(Language):
    Defaults = ArabicDefaults
    lang = "ar"


__all__ = ["Arabic"]
