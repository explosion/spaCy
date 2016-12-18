# encoding: utf8
from __future__ import unicode_literals, print_function

from os import path

from ..language import Language
from ..attrs import LANG

from .language_data import *


class German(Language):
    lang = 'de'

    class Defaults(Language.Defaults):
        tokenizer_exceptions = dict(language_data.TOKENIZER_EXCEPTIONS)
        lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
        lex_attr_getters[LANG] = lambda text: 'de'

        tokenizer_exceptions = TOKENIZER_EXCEPTIONS
        tag_map = TAG_MAP
        stop_words = STOP_WORDS
