# coding: utf8
from __future__ import unicode_literals

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS, TOKEN_MATCH
from .punctuation import TOKENIZER_SUFFIXES, TOKENIZER_INFIXES
from .stop_words import STOP_WORDS
from .lemmatizer import LOOKUP

from ..language_data import BASE_EXCEPTIONS
from ..language import Language
from ..lemmatizerlookup import Lemmatizer
from ..attrs import LANG
from ..util import update_exc


class French(Language):
    lang = 'fr'

    class Defaults(Language.Defaults):
        lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
        lex_attr_getters[LANG] = lambda text: 'fr'

        tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
        stop_words = set(STOP_WORDS)
        infixes = tuple(TOKENIZER_INFIXES)
        suffixes = tuple(TOKENIZER_SUFFIXES)
        token_match = TOKEN_MATCH

        @classmethod
        def create_lemmatizer(cls, nlp=None):
            return Lemmatizer(LOOKUP)


__all__ = ['French']
