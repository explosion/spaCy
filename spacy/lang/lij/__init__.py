from ...language import BaseDefaults, Language
from .punctuation import TOKENIZER_INFIXES
from .stop_words import STOP_WORDS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS


class LigurianDefaults(BaseDefaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    infixes = TOKENIZER_INFIXES
    stop_words = STOP_WORDS


class Ligurian(Language):
    lang = "lij"
    Defaults = LigurianDefaults


__all__ = ["Ligurian"]
