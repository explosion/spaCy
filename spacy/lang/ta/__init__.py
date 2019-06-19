# coding: utf8
from __future__ import unicode_literals

from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS

from ...language import Language
from ...attrs import LANG


class TamilDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: "ta"
    lex_attr_getters.update(LEX_ATTRS)
    stop_words = STOP_WORDS


class Tamil(Language):
    lang = "ta"
    Defaults = TamilDefaults


__all__ = ["Tamil"]
