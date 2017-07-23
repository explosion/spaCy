# coding: utf8
from __future__ import unicode_literals

from .stop_words import STOP_WORDS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .lex_attrs import LEX_ATTRS

from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...language import Language
from ...attrs import LANG
from ...util import update_exc


class IndonesianDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: 'id'

    lex_attr_getters.update(LEX_ATTRS)

    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    stop_words = set(STOP_WORDS)


class Indonesian(Language):
    lang = 'id'
    Defaults = IndonesianDefaults


__all__ = ['Indonesian']
