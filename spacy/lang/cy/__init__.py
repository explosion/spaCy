# coding: utf8
from __future__ import unicode_literals

from .lex_attrs import LEX_ATTRS
from .stop_words import STOP_WORDS


from ...language import Language
from ...attrs import LANG


class WelshDefaults(Language.Defaults):

    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters.update(LEX_ATTRS)
    lex_attr_getters[LANG] = lambda text: "cy"

    stop_words = STOP_WORDS


class Welsh(Language):
    lang = "cy"
    Defaults = WelshDefaults


__all__ = ["Welsh"]
