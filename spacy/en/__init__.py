# coding: utf8
from __future__ import unicode_literals

from ..language import Language
from ..lemmatizer import Lemmatizer
from ..vocab import Vocab
from ..tokenizer import Tokenizer
from ..attrs import LANG
from ..deprecated import fix_glove_vectors_loading

from .language_data import *


try:
    basestring
except NameError:
    basestring = str


class English(Language):
    lang = 'en'

    class Defaults(Language.Defaults):
        lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
        lex_attr_getters[LANG] = lambda text: 'en'

        tokenizer_exceptions = TOKENIZER_EXCEPTIONS
        tag_map = TAG_MAP
        stop_words = STOP_WORDS

        morph_rules = dict(MORPH_RULES)
        lemma_rules = dict(LEMMA_RULES)
        lemma_index = dict(LEMMA_INDEX)
        lemma_exc = dict(LEMMA_EXC)


    def __init__(self, **overrides):
        # Special-case hack for loading the GloVe vectors, to support <1.0
        overrides = fix_glove_vectors_loading(overrides)
        Language.__init__(self, **overrides)
