# coding: utf8
from __future__ import unicode_literals

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .lemmatizer import LOOKUP

from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...language import Language
from ...lemmatizerlookup import Lemmatizer
from ...attrs import LANG
from ...util import update_exc


class Portuguese(Language):
    lang = 'pt'

    class Defaults(Language.Defaults):
        lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
        lex_attr_getters[LANG] = lambda text: 'pt'
        lex_attr_getters.update(LEX_ATTRS)

        tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
        stop_words = set(STOP_WORDS)

        @classmethod
        def create_lemmatizer(cls, nlp=None):
            return Lemmatizer(LOOKUP)


__all__ = ['Portuguese']
