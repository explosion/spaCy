from ...language import BaseDefaults, Language
from .lex_attrs import LEX_ATTRS
from .punctuation import TOKENIZER_INFIXES, TOKENIZER_SUFFIXES
from .stop_words import STOP_WORDS
from .syntax_iterators import SYNTAX_ITERATORS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS


class FinnishDefaults(BaseDefaults):
    infixes = TOKENIZER_INFIXES
    suffixes = TOKENIZER_SUFFIXES
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    lex_attr_getters = LEX_ATTRS
    stop_words = STOP_WORDS
    syntax_iterators = SYNTAX_ITERATORS


class Finnish(Language):
    lang = "fi"
    Defaults = FinnishDefaults


__all__ = ["Finnish"]
