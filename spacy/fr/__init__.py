# encoding: utf8
from __future__ import unicode_literals, print_function

from ..language import Language, BaseDefaults
from ..attrs import LANG

from .language_data import *
from .punctuation import TOKENIZER_INFIXES, TOKENIZER_SUFFIXES


class FrenchDefaults(BaseDefaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: 'fr'

    stop_words = STOP_WORDS
    infixes = tuple(TOKENIZER_INFIXES)
    suffixes = tuple(TOKENIZER_SUFFIXES)
    token_match = TOKEN_MATCH

    @classmethod
    def create_tokenizer(cls, nlp=None):
        cls.tokenizer_exceptions = get_tokenizer_exceptions()
        return super(FrenchDefaults, cls).create_tokenizer(nlp)


class French(Language):
    lang = 'fr'

    Defaults = FrenchDefaults
