from .punctuation import TOKENIZER_INFIXES, TOKENIZER_SUFFIXES
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from ...language import Language, BaseDefaults


class LithuanianDefaults(BaseDefaults):
    infixes = TOKENIZER_INFIXES
    suffixes = TOKENIZER_SUFFIXES
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    stop_words = STOP_WORDS
    lex_attr_getters = LEX_ATTRS


class Lithuanian(Language):
    lang = "lt"
    Defaults = LithuanianDefaults


__all__ = ["Lithuanian"]
