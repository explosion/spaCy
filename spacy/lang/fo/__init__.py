import spacy
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from spacy.lang.punctuation import (
    TOKENIZER_SUFFIXES,
    TOKENIZER_PREFIXES,
    TOKENIZER_INFIXES,
)

from spacy.language import Language, BaseDefaults


class FaroeseDefaults(BaseDefaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    infixes = TOKENIZER_INFIXES
    suffixes = TOKENIZER_SUFFIXES
    prefixes = TOKENIZER_PREFIXES


@spacy.registry.languages("fo")
class Faroese(Language):
    lang = "fo"
    Defaults = FaroeseDefaults


__all__ = ["Faroese"]
