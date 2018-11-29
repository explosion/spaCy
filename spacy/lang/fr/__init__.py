# coding: utf8
from __future__ import unicode_literals

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS, TOKEN_MATCH
from .punctuation import TOKENIZER_SUFFIXES, TOKENIZER_INFIXES
from .tag_map import TAG_MAP
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .lemmatizer import LEMMA_RULES, LEMMA_INDEX, LEMMA_EXC, LOOKUP
from .lemmatizer.lemmatizer import FrenchLemmatizer
from .syntax_iterators import SYNTAX_ITERATORS

from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ..norm_exceptions import BASE_NORMS
from ...language import Language
from ...attrs import LANG, NORM
from ...util import update_exc, add_lookups


class FrenchDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters.update(LEX_ATTRS)
    lex_attr_getters[LANG] = lambda text: 'fr'
    lex_attr_getters[NORM] = add_lookups(Language.Defaults.lex_attr_getters[NORM], BASE_NORMS)
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    tag_map = TAG_MAP
    stop_words = STOP_WORDS
    infixes = TOKENIZER_INFIXES
    suffixes = TOKENIZER_SUFFIXES
    token_match = TOKEN_MATCH
    syntax_iterators = SYNTAX_ITERATORS
    
    
    @classmethod
    def create_lemmatizer(cls, nlp=None):
        lemma_rules = LEMMA_RULES
        lemma_index = LEMMA_INDEX
        lemma_exc = LEMMA_EXC
        lemma_lookup = LOOKUP
        return FrenchLemmatizer(index=lemma_index, exceptions=lemma_exc,
                                rules=lemma_rules, lookup=lemma_lookup)


class French(Language):
    lang = 'fr'
    Defaults = FrenchDefaults


__all__ = ['French']
