# coding: utf8
from __future__ import unicode_literals

from .stop_words import STOP_WORDS

from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...language import Language
from ...attrs import LANG
from ...util import update_exc


class HebrewDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: "he"
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS)
    stop_words = STOP_WORDS
    writing_system = {"direction": "rtl", "has_case": False, "has_letters": True}


class Hebrew(Language):
    lang = "he"
    Defaults = HebrewDefaults


__all__ = ["Hebrew"]
