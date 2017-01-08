# encoding: utf8
from __future__ import unicode_literals, print_function

from ..language import Language
from ..attrs import LANG
from .language_data import *


class Dutch(Language):
    lang = 'nl'

    class Defaults(Language.Defaults):
        lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
        lex_attr_getters[LANG] = lambda text: 'nl'

        tokenizer_exceptions = TOKENIZER_EXCEPTIONS
        stop_words = STOP_WORDS
