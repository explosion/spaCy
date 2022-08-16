from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .punctuation import TOKENIZER_INFIXES
from .lex_attrs import LEX_ATTRS
from ...language import Language, BaseDefaults


class LuxembourgishDefaults(BaseDefaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    infixes = TOKENIZER_INFIXES
    lex_attr_getters = LEX_ATTRS


class Luxembourgish(Language):
    lang = "lb"
    Defaults = LuxembourgishDefaults


__all__ = ["Luxembourgish"]
