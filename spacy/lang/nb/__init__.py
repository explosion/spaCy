from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .punctuation import TOKENIZER_PREFIXES, TOKENIZER_INFIXES
from .punctuation import TOKENIZER_SUFFIXES
from .stop_words import STOP_WORDS
from .syntax_iterators import SYNTAX_ITERATORS
from ...language import Language


class NorwegianDefaults(Language.Defaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    prefixes = TOKENIZER_PREFIXES
    infixes = TOKENIZER_INFIXES
    suffixes = TOKENIZER_SUFFIXES
    syntax_iterators = SYNTAX_ITERATORS
    stop_words = STOP_WORDS


class Norwegian(Language):
    lang = "nb"
    Defaults = NorwegianDefaults


__all__ = ["Norwegian"]
