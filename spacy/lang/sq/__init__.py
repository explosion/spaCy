# coding: utf8
from __future__ import unicode_literals

from .stop_words import STOP_WORDS
from ...language import Language
from ...attrs import LANG


class AlbanianDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: "sq"
    stop_words = STOP_WORDS


class Albanian(Language):
    lang = "sq"
    Defaults = AlbanianDefaults


__all__ = ["Albanian"]
