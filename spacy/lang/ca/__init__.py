from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .punctuation import TOKENIZER_INFIXES
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from ...language import Language


class CatalanDefaults(Language.Defaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    infixes = TOKENIZER_INFIXES
    stop_words = STOP_WORDS
    lex_attr_getters = LEX_ATTRS


class Catalan(Language):
    lang = "ca"
    Defaults = CatalanDefaults


__all__ = ["Catalan"]
