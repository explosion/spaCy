# encoding: utf8
from __future__ import unicode_literals, print_function

from os import path

from ..language import Language
from ..attrs import LANG


# Import language-specific data
from .language_data import *


# create Language subclass
class Norwegian(Language):
    lang = 'nb' # ISO code

    class Defaults(Language.Defaults):
        lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
        lex_attr_getters[LANG] = lambda text: 'nb'
        
        # override defaults
        tokenizer_exceptions = TOKENIZER_EXCEPTIONS
        #tag_map = TAG_MAP
        stop_words = STOP_WORDS
