from .lex_attrs import LEX_ATTRS
from .stop_words import STOP_WORDS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from ...language import Language, BaseDefaults


class UpperSorbianDefaults(BaseDefaults):
    lex_attr_getters = LEX_ATTRS
    stop_words = STOP_WORDS
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS


class UpperSorbian(Language):
    lang = "hsb"
    Defaults = UpperSorbianDefaults


__all__ = ["UpperSorbian"]
