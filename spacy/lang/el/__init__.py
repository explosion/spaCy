# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .tag_map_general import TAG_MAP
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .lemmatizer import LEMMA_RULES, LEMMA_INDEX, LEMMA_EXC
from .punctuation import TOKENIZER_PREFIXES, TOKENIZER_SUFFIXES, TOKENIZER_INFIXES
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from .norm_exceptions import NORM_EXCEPTIONS
from ..norm_exceptions import BASE_NORMS
from ...language import Language
from ...attrs import LANG, NORM
from ...util import update_exc, add_lookups


class GreekDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters.update(LEX_ATTRS)
    lex_attr_getters[LANG] = lambda text: 'el'  # ISO code
    lex_attr_getters[NORM] = add_lookups(Language.Defaults.lex_attr_getters[NORM], BASE_NORMS, NORM_EXCEPTIONS)
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    stop_words = STOP_WORDS
    lemma_rules = LEMMA_RULES
    lemma_index = LEMMA_INDEX
    tag_map = TAG_MAP
    prefixes = TOKENIZER_PREFIXES
    suffixes = TOKENIZER_SUFFIXES
    infixes = TOKENIZER_INFIXES


class Greek(Language):

    lang = 'el'  # ISO code
    Defaults = GreekDefaults  # set Defaults to custom language defaults


# set default export – this allows the language class to be lazy-loaded
__all__ = ['Greek']

