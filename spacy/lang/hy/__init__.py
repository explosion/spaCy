from .lex_attrs import LEX_ATTRS
from ...language import Language, BaseDefaults


class ArmenianDefaults(BaseDefaults):
    lex_attr_getters = LEX_ATTRS


class Armenian(Language):
    lang = "hy"
    Defaults = ArmenianDefaults


__all__ = ["Armenian"]
