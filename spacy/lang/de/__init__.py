# coding: utf8
from __future__ import unicode_literals

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .norm_exceptions import NORM_EXCEPTIONS
from .tag_map import TAG_MAP
from .stop_words import STOP_WORDS
from .lemmatizer import LOOKUP
from .syntax_iterators import SYNTAX_ITERATORS

from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ..norm_exceptions import BASE_NORMS
from ...language import Language
from ...lemmatizerlookup import Lemmatizer
from ...attrs import LANG, NORM
from ...util import update_exc, add_lookups


class GermanDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: 'de'
    lex_attr_getters[NORM] = add_lookups(Language.Defaults.lex_attr_getters[NORM],
                                         NORM_EXCEPTIONS, BASE_NORMS)

    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    tag_map = dict(TAG_MAP)
    stop_words = set(STOP_WORDS)
    syntax_iterators = dict(SYNTAX_ITERATORS)

    @classmethod
    def create_lemmatizer(cls, nlp=None):
        return Lemmatizer(LOOKUP)


class German(Language):
    lang = 'de'
    Defaults = GermanDefaults


__all__ = ['German']
