# coding: utf8
from __future__ import unicode_literals

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS
from .morph_rules import MORPH_RULES
from .lemmatizer import LEMMA_RULES, LOOKUP

from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...language import Language
from ...lemmatizerlookup import Lemmatizer
from ...attrs import LANG
from ...util import update_exc


class Swedish(Language):
    lang = 'sv'

    class Defaults(Language.Defaults):
        lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
        lex_attr_getters[LANG] = lambda text: 'sv'

        tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
        stop_words = set(STOP_WORDS)

        @classmethod
        def create_lemmatizer(cls, nlp=None):
            return Lemmatizer(LOOKUP)


__all__ = ['Swedish']
