# coding: utf8
from __future__ import unicode_literals

from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...language import Language
from ...attrs import LANG


class YorubaDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters.update(LEX_ATTRS)
    lex_attr_getters[LANG] = lambda text: "yo"
    stop_words = STOP_WORDS
    tokenizer_exceptions = BASE_EXCEPTIONS


class Yoruba(Language):
    lang = "yo"
    Defaults = YorubaDefaults


__all__ = ["Yoruba"]
