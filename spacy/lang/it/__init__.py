# coding: utf8
from __future__ import unicode_literals

from .stop_words import STOP_WORDS
from .lemmatizer import LOOKUP

from ..language_data import BASE_EXCEPTIONS
from ..language import Language
from ..lemmatizerlookup import Lemmatizer
from ..attrs import LANG
from ..util import update_exc


class Italian(Language):
    lang = 'it'

    class Defaults(Language.Defaults):
        lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
        lex_attr_getters[LANG] = lambda text: 'it'

        tokenizer_exceptions = update_exc(BASE_EXCEPTIONS)
        stop_words = set(STOP_WORDS)

        @classmethod
        def create_lemmatizer(cls, nlp=None):
            return Lemmatizer(LOOKUP)


__all__ = ['Italian']
