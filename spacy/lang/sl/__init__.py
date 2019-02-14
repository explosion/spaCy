# coding: utf8
from __future__ import unicode_literals

from .stop_words import STOP_WORDS
from ...language import Language
from ...attrs import LANG


class SlovenianDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: "sl"
    stop_words = STOP_WORDS


class Slovenian(Language):
    lang = "sl"
    Defaults = SlovenianDefaults


__all__ = ["Slovenian"]
