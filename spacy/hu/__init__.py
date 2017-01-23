# encoding: utf8
from __future__ import unicode_literals, print_function

from .tokenizer_exceptions import TOKEN_MATCH
from .language_data import *
from ..attrs import LANG
from ..language import Language


class Hungarian(Language):
    lang = 'hu'

    class Defaults(Language.Defaults):
        tokenizer_exceptions = dict(TOKENIZER_EXCEPTIONS)
        lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
        lex_attr_getters[LANG] = lambda text: 'hu'

        prefixes = tuple(TOKENIZER_PREFIXES)

        suffixes = tuple(TOKENIZER_SUFFIXES)

        infixes = tuple(TOKENIZER_INFIXES)

        stop_words = set(STOP_WORDS)

        token_match = TOKEN_MATCH
