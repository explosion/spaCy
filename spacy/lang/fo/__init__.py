from ...language import BaseDefaults, Language
from ..punctuation import TOKENIZER_INFIXES, TOKENIZER_PREFIXES, TOKENIZER_SUFFIXES
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS


class FaroeseDefaults(BaseDefaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    infixes = TOKENIZER_INFIXES
    suffixes = TOKENIZER_SUFFIXES
    prefixes = TOKENIZER_PREFIXES


class Faroese(Language):
    lang = "fo"
    Defaults = FaroeseDefaults


__all__ = ["Faroese"]
