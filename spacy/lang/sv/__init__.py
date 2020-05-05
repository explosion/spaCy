# coding: utf8
from __future__ import unicode_literals

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .tag_map import TAG_MAP
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .morph_rules import MORPH_RULES

# Punctuation stolen from Danish
from ..da.punctuation import TOKENIZER_INFIXES, TOKENIZER_SUFFIXES

from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ..norm_exceptions import BASE_NORMS
from ...language import Language
from ...attrs import LANG, NORM
from ...util import update_exc, add_lookups
from .syntax_iterators import SYNTAX_ITERATORS


class SwedishDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters.update(LEX_ATTRS)
    lex_attr_getters[LANG] = lambda text: "sv"
    lex_attr_getters[NORM] = add_lookups(
        Language.Defaults.lex_attr_getters[NORM], BASE_NORMS
    )
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    morph_rules = MORPH_RULES
    tag_map = TAG_MAP
    infixes = TOKENIZER_INFIXES
    suffixes = TOKENIZER_SUFFIXES
    stop_words = STOP_WORDS
    morph_rules = MORPH_RULES
    syntax_iterators = SYNTAX_ITERATORS


class Swedish(Language):
    lang = "sv"
    Defaults = SwedishDefaults


__all__ = ["Swedish"]
