# coding: utf8
from __future__ import unicode_literals

from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from ..tag_map import TAG_MAP

from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...language import Language
from ...attrs import LANG

from .punctuation import TOKENIZER_SUFFIXES


class UrduDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters.update(LEX_ATTRS)
    lex_attr_getters[LANG] = lambda text: "ur"

    tokenizer_exceptions = BASE_EXCEPTIONS
    tag_map = TAG_MAP
    stop_words = STOP_WORDS
    suffixes = TOKENIZER_SUFFIXES


class Urdu(Language):
    lang = "ur"
    Defaults = UrduDefaults


__all__ = ["Urdu"]
