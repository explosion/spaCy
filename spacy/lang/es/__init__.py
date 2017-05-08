# coding: utf8
from __future__ import unicode_literals

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .tag_map import TAG_MAP
from .stop_words import STOP_WORDS
from .lemmatizer import LOOKUP

from ..language_data import BASE_EXCEPTIONS
from ..language import Language
from ..lemmatizerlookup import Lemmatizer
from ..attrs import LANG
from ..util import update_exc


class Spanish(Language):
    lang = 'es'

    class Defaults(Language.Defaults):
        lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
        lex_attr_getters[LANG] = lambda text: 'es'

        tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
        tag_map = dict(TAG_MAP)
        stop_words = set(STOP_WORDS)

        @classmethod
        def create_lemmatizer(cls, nlp=None):
            return Lemmatizer(LOOKUP)


__all__ = ['Spanish']
