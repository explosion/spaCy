from .stop_words import STOP_WORDS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .punctuation import TOKENIZER_PREFIXES, TOKENIZER_INFIXES
from ...language import Language


class ItalianDefaults(Language.Defaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    stop_words = STOP_WORDS
    prefixes = TOKENIZER_PREFIXES
    infixes = TOKENIZER_INFIXES


class Italian(Language):
    lang = "it"
    Defaults = ItalianDefaults


__all__ = ["Italian"]
