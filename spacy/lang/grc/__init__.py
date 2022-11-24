from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .punctuation import TOKENIZER_PREFIXES, TOKENIZER_SUFFIXES, TOKENIZER_INFIXES
from ...language import Language, BaseDefaults


class AncientGreekDefaults(BaseDefaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    prefixes = TOKENIZER_PREFIXES
    suffixes = TOKENIZER_SUFFIXES
    infixes = TOKENIZER_INFIXES
    lex_attr_getters = LEX_ATTRS
    stop_words = STOP_WORDS


class AncientGreek(Language):
    lang = "grc"
    Defaults = AncientGreekDefaults


__all__ = ["AncientGreek"]
