from .lex_attrs import LEX_ATTRS
from .stop_words import STOP_WORDS
from ...language import Language, BaseDefaults


class LowerSorbianDefaults(BaseDefaults):
    lex_attr_getters = LEX_ATTRS
    stop_words = STOP_WORDS


class LowerSorbian(Language):
    lang = "dsb"
    Defaults = LowerSorbianDefaults


__all__ = ["LowerSorbian"]
