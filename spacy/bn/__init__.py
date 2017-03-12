# coding: utf8
from __future__ import unicode_literals, print_function

from ..language import Language
from ..attrs import LANG

from .language_data import *


class Bengali(Language):
    lang = 'bn'

    class Defaults(Language.Defaults):
        lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
        lex_attr_getters[LANG] = lambda text: 'bn'

        tokenizer_exceptions = TOKENIZER_EXCEPTIONS
        tag_map = TAG_MAP
        stop_words = STOP_WORDS
        lemma_rules = LEMMA_RULES

        prefixes = tuple(TOKENIZER_PREFIXES)
        suffixes = tuple(TOKENIZER_SUFFIXES)
        infixes = tuple(TOKENIZER_INFIXES)
