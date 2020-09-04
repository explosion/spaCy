from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .punctuation import TOKENIZER_SUFFIXES
from .syntax_iterators import SYNTAX_ITERATORS
from ...language import Language


class PersianDefaults(Language.Defaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    suffixes = TOKENIZER_SUFFIXES
    lex_attr_getters = LEX_ATTRS
    syntax_iterators = SYNTAX_ITERATORS
    stop_words = STOP_WORDS
    writing_system = {"direction": "rtl", "has_case": False, "has_letters": True}


class Persian(Language):
    lang = "fa"
    Defaults = PersianDefaults


__all__ = ["Persian"]
