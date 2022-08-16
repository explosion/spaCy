from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .lex_attrs import LEX_ATTRS
from .punctuation import TOKENIZER_INFIXES, TOKENIZER_SUFFIXES
from .syntax_iterators import SYNTAX_ITERATORS
from ...language import Language, BaseDefaults


class FinnishDefaults(BaseDefaults):
    infixes = TOKENIZER_INFIXES
    suffixes = TOKENIZER_SUFFIXES
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    lex_attr_getters = LEX_ATTRS
    syntax_iterators = SYNTAX_ITERATORS


class Finnish(Language):
    lang = "fi"
    Defaults = FinnishDefaults


__all__ = ["Finnish"]
