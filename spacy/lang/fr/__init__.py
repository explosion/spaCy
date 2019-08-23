# coding: utf8
from __future__ import unicode_literals

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS, TOKEN_MATCH
from .punctuation import TOKENIZER_SUFFIXES, TOKENIZER_INFIXES
from .tag_map import TAG_MAP
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .lemmatizer import FrenchLemmatizer
from .syntax_iterators import SYNTAX_ITERATORS

from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ..norm_exceptions import BASE_NORMS
from ...language import Language
from ...attrs import LANG, NORM
from ...util import update_exc, add_lookups, get_lemma_tables


class FrenchDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters.update(LEX_ATTRS)
    lex_attr_getters[LANG] = lambda text: "fr"
    lex_attr_getters[NORM] = add_lookups(
        Language.Defaults.lex_attr_getters[NORM], BASE_NORMS
    )
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    tag_map = TAG_MAP
    stop_words = STOP_WORDS
    infixes = TOKENIZER_INFIXES
    suffixes = TOKENIZER_SUFFIXES
    token_match = TOKEN_MATCH
    syntax_iterators = SYNTAX_ITERATORS
    resources = {
        "lemma_rules": "lemmatizer/lemma_rules.json",
        "lemma_index": "lemmatizer/lemma_index.json",
        "lemma_exc": "lemmatizer/lemma_exc.json",
        "lemma_lookup": "lemmatizer/lemma_lookup.json",
    }

    @classmethod
    def create_lemmatizer(cls, nlp=None, lookups=None):
        lemma_rules, lemma_index, lemma_exc, lemma_lookup = get_lemma_tables(lookups)
        return FrenchLemmatizer(lemma_index, lemma_exc, lemma_rules, lemma_lookup)


class French(Language):
    lang = "fr"
    Defaults = FrenchDefaults


__all__ = ["French"]
