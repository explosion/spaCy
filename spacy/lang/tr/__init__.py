from ...language import BaseDefaults, Language
from .lex_attrs import LEX_ATTRS
from .stop_words import STOP_WORDS
from .syntax_iterators import SYNTAX_ITERATORS
from .tokenizer_exceptions import TOKEN_MATCH, TOKENIZER_EXCEPTIONS


class TurkishDefaults(BaseDefaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    lex_attr_getters = LEX_ATTRS
    stop_words = STOP_WORDS
    token_match = TOKEN_MATCH
    syntax_iterators = SYNTAX_ITERATORS


class Turkish(Language):
    lang = "tr"
    Defaults = TurkishDefaults


__all__ = ["Turkish"]
