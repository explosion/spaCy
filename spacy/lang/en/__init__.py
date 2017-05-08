# coding: utf8
from __future__ import unicode_literals

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .tag_map import TAG_MAP
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .morph_rules import MORPH_RULES
from .lemmatizer import LEMMA_RULES, LEMMA_INDEX, LEMMA_EXC

from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...language import Language
from ...attrs import LANG
from ...util import update_exc


class English(Language):
    lang = 'en'

    class Defaults(Language.Defaults):
        lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
        lex_attr_getters[LANG] = lambda text: 'en'
        lex_attr_getters.update(LEX_ATTRS)

        tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
        tag_map = dict(TAG_MAP)
        stop_words = set(STOP_WORDS)
        morph_rules = dict(MORPH_RULES)
        lemma_rules = dict(LEMMA_RULES)
        lemma_index = dict(LEMMA_INDEX)
        lemma_exc = dict(LEMMA_EXC)


__all__ = ['English']
