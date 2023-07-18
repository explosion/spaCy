from ...language import BaseDefaults, Language
from .punctuation import TOKENIZER_INFIXES, TOKENIZER_PREFIXES, TOKENIZER_SUFFIXES
from .stop_words import STOP_WORDS
from .tokenizer_exceptions import TOKEN_MATCH, TOKENIZER_EXCEPTIONS


class HungarianDefaults(BaseDefaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    prefixes = TOKENIZER_PREFIXES
    suffixes = TOKENIZER_SUFFIXES
    infixes = TOKENIZER_INFIXES
    token_match = TOKEN_MATCH
    stop_words = STOP_WORDS


class Hungarian(Language):
    lang = "hu"
    Defaults = HungarianDefaults


__all__ = ["Hungarian"]
