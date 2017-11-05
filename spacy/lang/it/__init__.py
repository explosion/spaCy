# coding: utf8
from __future__ import unicode_literals

from .stop_words import STOP_WORDS
from .lemmatizer import LOOKUP
from .tag_map import TAG_MAP

from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ..norm_exceptions import BASE_NORMS
from ...language import Language
from ...attrs import LANG, NORM
from ...util import update_exc, add_lookups


class ItalianDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: 'it'
    lex_attr_getters[NORM] = add_lookups(Language.Defaults.lex_attr_getters[NORM], BASE_NORMS)
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS)
    stop_words = STOP_WORDS
    lemma_lookup = LOOKUP
    tag_map = TAG_MAP


class Italian(Language):
    lang = 'it'
    Defaults = ItalianDefaults


__all__ = ['Italian']
