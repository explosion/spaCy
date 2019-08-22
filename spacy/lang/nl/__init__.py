# coding: utf8
from __future__ import unicode_literals

from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .tag_map import TAG_MAP
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .punctuation import TOKENIZER_INFIXES, TOKENIZER_SUFFIXES
from .lemmatizer import DutchLemmatizer
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ..norm_exceptions import BASE_NORMS
from ...language import Language
from ...attrs import LANG, NORM
from ...util import update_exc, add_lookups, get_lemma_tables


class DutchDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters.update(LEX_ATTRS)
    lex_attr_getters[LANG] = lambda text: "nl"
    lex_attr_getters[NORM] = add_lookups(
        Language.Defaults.lex_attr_getters[NORM], BASE_NORMS
    )
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    stop_words = STOP_WORDS
    tag_map = TAG_MAP
    infixes = TOKENIZER_INFIXES
    suffixes = TOKENIZER_SUFFIXES
    resources = {
        "lemma_rules": "lemmatizer/lemma_rules.json",
        "lemma_index": "lemmatizer/lemma_index.json",
        "lemma_exc": "lemmatizer/lemma_exc.json",
        "lemma_lookup": "lemmatizer/lemma_lookup.json",
    }

    @classmethod
    def create_lemmatizer(cls, nlp=None, lookups=None):
        lemma_rules, lemma_index, lemma_exc, lemma_lookup = get_lemma_tables(lookups)
        return DutchLemmatizer(lemma_index, lemma_exc, lemma_rules, lemma_lookup)


class Dutch(Language):
    lang = "nl"
    Defaults = DutchDefaults


__all__ = ["Dutch"]
