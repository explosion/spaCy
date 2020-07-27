from .stop_words import STOP_WORDS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .punctuation import TOKENIZER_INFIXES
from ...language import Language


class LigurianDefaults(Language.Defaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    infixes = TOKENIZER_INFIXES
    stop_words = STOP_WORDS


class Ligurian(Language):
    lang = "lij"
    Defaults = LigurianDefaults


__all__ = ["Ligurian"]
