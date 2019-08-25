# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .tag_map_general import TAG_MAP
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .lemmatizer import GreekLemmatizer
from .syntax_iterators import SYNTAX_ITERATORS
from .punctuation import TOKENIZER_PREFIXES, TOKENIZER_SUFFIXES, TOKENIZER_INFIXES
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from .norm_exceptions import NORM_EXCEPTIONS
from ..norm_exceptions import BASE_NORMS
from ...language import Language
from ...attrs import LANG, NORM
from ...util import update_exc, add_lookups, get_lemma_tables


class GreekDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters.update(LEX_ATTRS)
    lex_attr_getters[LANG] = lambda text: "el"
    lex_attr_getters[NORM] = add_lookups(
        Language.Defaults.lex_attr_getters[NORM], BASE_NORMS, NORM_EXCEPTIONS
    )
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    stop_words = STOP_WORDS
    tag_map = TAG_MAP
    prefixes = TOKENIZER_PREFIXES
    suffixes = TOKENIZER_SUFFIXES
    infixes = TOKENIZER_INFIXES
    syntax_iterators = SYNTAX_ITERATORS
    resources = {
        "lemma_index": "lemmatizer/lemma_index.json",
        "lemma_exc": "lemmatizer/lemma_exc.json",
        "lemma_rules": "lemmatizer/lemma_rules.json",
    }

    @classmethod
    def create_lemmatizer(cls, nlp=None, lookups=None):
        lemma_rules, lemma_index, lemma_exc, lemma_lookup = get_lemma_tables(lookups)
        return GreekLemmatizer(lemma_index, lemma_exc, lemma_rules, lemma_lookup)


class Greek(Language):
    lang = "el"
    Defaults = GreekDefaults


__all__ = ["Greek"]
