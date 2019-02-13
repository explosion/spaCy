# coding: utf8
from __future__ import unicode_literals

from .stop_words import STOP_WORDS
from ...language import Language
from ...attrs import LANG


class KannadaDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: "kn"
    stop_words = STOP_WORDS


class Kannada(Language):
    lang = "kn"
    Defaults = KannadaDefaults


__all__ = ["Kannada"]
