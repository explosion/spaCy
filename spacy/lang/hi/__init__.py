# coding: utf8
from __future__ import unicode_literals

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS

from ...language import Language
from ...attrs import LANG
from ...util import update_exc


class HindiDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters.update(LEX_ATTRS)
    lex_attr_getters[LANG] = lambda text: "hi"
    tokenizer_exceptions = update_exc(TOKENIZER_EXCEPTIONS)
    stop_words = STOP_WORDS


class Hindi(Language):
    lang = "hi"
    Defaults = HindiDefaults


__all__ = ["Hindi"]
