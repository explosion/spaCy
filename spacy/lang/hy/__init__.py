from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS

from ...attrs import LANG
from ...language import Language


class ArmenianDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: "hy"

    lex_attr_getters.update(LEX_ATTRS)
    stop_words = STOP_WORDS


class Armenian(Language):
    lang = "hy"
    Defaults = ArmenianDefaults


__all__ = ["Armenian"]
