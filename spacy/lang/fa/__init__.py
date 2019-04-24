# coding: utf8
from __future__ import unicode_literals

from ...language import Language
from ...attrs import LANG, NORM
from ...util import update_exc, add_lookups
from ..norm_exceptions import BASE_NORMS
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .tag_map import TAG_MAP
from .punctuation import TOKENIZER_SUFFIXES
from .lemmatizer import LEMMA_RULES, LEMMA_INDEX, LEMMA_EXC


class PersianDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters.update(LEX_ATTRS)
    lex_attr_getters[NORM] = add_lookups(
        Language.Defaults.lex_attr_getters[NORM], BASE_NORMS
    )
    lex_attr_getters[LANG] = lambda text: "fa"
    tokenizer_exceptions = update_exc(TOKENIZER_EXCEPTIONS)
    lemma_rules = LEMMA_RULES
    lemma_index = LEMMA_INDEX
    lemma_exc = LEMMA_EXC
    stop_words = STOP_WORDS
    tag_map = TAG_MAP
    suffixes = TOKENIZER_SUFFIXES
    writing_system = {"direction": "rtl", "has_case": False, "has_letters": True}


class Persian(Language):
    lang = "fa"
    Defaults = PersianDefaults


__all__ = ["Persian"]
