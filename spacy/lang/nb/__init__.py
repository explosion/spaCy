# coding: utf8
from __future__ import unicode_literals

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS
from .morph_rules import MORPH_RULES

from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ..norm_exceptions import BASE_NORMS
from .lemmatizer import LOOKUP
from .tag_map import TAG_MAP
from ...language import Language
from ...attrs import LANG, NORM
from ...util import update_exc, add_lookups

# Borrowing french syntax parser because both languages use
# universal dependencies for tagging/parsing.
# Read here for more:
# https://github.com/explosion/spaCy/pull/1882#issuecomment-361409573
from .syntax_iterators import SYNTAX_ITERATORS


class NorwegianDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: 'nb'
    lex_attr_getters[NORM] = add_lookups(Language.Defaults.lex_attr_getters[NORM], BASE_NORMS)
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    stop_words = STOP_WORDS
    tag_map = TAG_MAP
    lemma_lookup = LOOKUP
    syntax_iterators = SYNTAX_ITERATORS


class Norwegian(Language):
    lang = 'nb'
    Defaults = NorwegianDefaults


__all__ = ['Norwegian']
