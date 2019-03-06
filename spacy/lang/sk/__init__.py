# coding: utf8
from __future__ import unicode_literals

from .stop_words import STOP_WORDS
from ...language import Language
from ...attrs import LANG


class SlovakDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: "sk"
    stop_words = STOP_WORDS


class Slovak(Language):
    lang = "sk"
    Defaults = SlovakDefaults


__all__ = ["Slovak"]
