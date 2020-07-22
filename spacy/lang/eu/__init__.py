# coding: utf8
from __future__ import unicode_literals

from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .punctuation import TOKENIZER_SUFFIXES

from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...language import Language
from ...attrs import LANG


class BasqueDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters.update(LEX_ATTRS)
    lex_attr_getters[LANG] = lambda text: "eu"

    tokenizer_exceptions = BASE_EXCEPTIONS
    stop_words = STOP_WORDS
    suffixes = TOKENIZER_SUFFIXES


class Basque(Language):
    lang = "eu"
    Defaults = BasqueDefaults


__all__ = ["Basque"]
