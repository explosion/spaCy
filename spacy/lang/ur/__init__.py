# coding: utf8
from __future__ import unicode_literals

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from ..tag_map import TAG_MAP

from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...language import Language
from ...attrs import LANG, NORM
from ...util import update_exc


class UrduDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters.update(LEX_ATTRS)
    lex_attr_getters[LANG] = lambda text: 'ur'

    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    tag_map = TAG_MAP
    stop_words = STOP_WORDS


class Urdu(Language):
    lang = 'ur'
    Defaults = UrduDefaults


__all__ = ['Urdu']
