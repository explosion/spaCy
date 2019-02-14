# coding: utf8
from __future__ import unicode_literals

from .stop_words import STOP_WORDS
from ...language import Language
from ...attrs import LANG


class LatvianDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: "lv"
    stop_words = STOP_WORDS


class Latvian(Language):
    lang = "lv"
    Defaults = LatvianDefaults


__all__ = ["Latvian"]
