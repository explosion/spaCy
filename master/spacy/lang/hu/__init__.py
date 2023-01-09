from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS, TOKEN_MATCH
from .punctuation import TOKENIZER_PREFIXES, TOKENIZER_SUFFIXES, TOKENIZER_INFIXES
from .stop_words import STOP_WORDS
from ...language import Language, BaseDefaults


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
