# coding: utf8
from __future__ import unicode_literals

from .stop_words import STOP_WORDS
from .tag_map import TAG_MAP
from .lex_attrs import LEX_ATTRS

from ...language import Language
from ...attrs import LANG


class SlovakDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters.update(LEX_ATTRS)
    lex_attr_getters[LANG] = lambda text: "sk"
    tag_map = TAG_MAP
    stop_words = STOP_WORDS


class Slovak(Language):
    lang = "sk"
    Defaults = SlovakDefaults


__all__ = ["Slovak"]
