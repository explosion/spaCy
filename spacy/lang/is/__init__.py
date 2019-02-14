# coding: utf8
from __future__ import unicode_literals

from .stop_words import STOP_WORDS
from ...language import Language
from ...attrs import LANG


class IcelandicDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: "is"
    stop_words = STOP_WORDS


class Icelandic(Language):
    lang = "is"
    Defaults = IcelandicDefaults


__all__ = ["Icelandic"]
