# encoding: utf8
from __future__ import unicode_literals, print_function

from os import path

from ..language import Language
from ..attrs import LANG
from .language_data import *


class Swedish(Language):
    lang = 'sv'

    class Defaults(Language.Defaults):
        lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
        lex_attr_getters[LANG] = lambda text: 'sv'

        tokenizer_exceptions = TOKENIZER_EXCEPTIONS
        stop_words = STOP_WORDS
