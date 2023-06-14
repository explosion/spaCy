from ...language import BaseDefaults, Language
from .lex_attrs import LEX_ATTRS
from .punctuation import TOKENIZER_INFIXES, TOKENIZER_PREFIXES, TOKENIZER_SUFFIXES
from .stop_words import STOP_WORDS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS

# Lemma data note:
# Original pairs downloaded from http://www.lexiconista.com/datasets/lemmatization/
# Replaced characters using cedillas with the correct ones (ș and ț)


class RomanianDefaults(BaseDefaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    prefixes = TOKENIZER_PREFIXES
    suffixes = TOKENIZER_SUFFIXES
    infixes = TOKENIZER_INFIXES
    lex_attr_getters = LEX_ATTRS
    stop_words = STOP_WORDS


class Romanian(Language):
    lang = "ro"
    Defaults = RomanianDefaults


__all__ = ["Romanian"]
