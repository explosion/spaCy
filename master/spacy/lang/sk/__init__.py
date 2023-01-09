from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from ...language import Language, BaseDefaults


class SlovakDefaults(BaseDefaults):
    lex_attr_getters = LEX_ATTRS
    stop_words = STOP_WORDS


class Slovak(Language):
    lang = "sk"
    Defaults = SlovakDefaults


__all__ = ["Slovak"]
