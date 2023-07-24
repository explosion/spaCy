from ...language import BaseDefaults, Language
from .lex_attrs import LEX_ATTRS
from .stop_words import STOP_WORDS
from .syntax_iterators import SYNTAX_ITERATORS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS


class LatinDefaults(BaseDefaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    stop_words = STOP_WORDS
    lex_attr_getters = LEX_ATTRS
    syntax_iterators = SYNTAX_ITERATORS


class Latin(Language):
    lang = "la"
    Defaults = LatinDefaults


__all__ = ["Latin"]
