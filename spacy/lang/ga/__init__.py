from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS
from ...language import Language


class IrishDefaults(Language.Defaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    stop_words = STOP_WORDS


class Irish(Language):
    lang = "ga"
    Defaults = IrishDefaults


__all__ = ["Irish"]
