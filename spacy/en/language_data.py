# coding: utf8
from __future__ import unicode_literals

from .. import language_data as base
from ..language_data import update_exc, strings_to_exc, expand_exc
from ..symbols import ORTH, LEMMA

from .tag_map import TAG_MAP
from .word_sets import STOP_WORDS, NUM_WORDS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS, ORTH_ONLY
from .morph_rules import MORPH_RULES
from .lemmatizer import RULES as LEMMA_RULES
from .lemmatizer import INDEX as LEMMA_INDEX
from .lemmatizer import EXC as LEMMA_EXC


TAG_MAP = dict(TAG_MAP)
STOP_WORDS = set(STOP_WORDS)


TOKENIZER_EXCEPTIONS = dict(TOKENIZER_EXCEPTIONS)
update_exc(TOKENIZER_EXCEPTIONS, strings_to_exc(ORTH_ONLY))
update_exc(TOKENIZER_EXCEPTIONS, expand_exc(TOKENIZER_EXCEPTIONS, "'", "’"))
update_exc(TOKENIZER_EXCEPTIONS, strings_to_exc(base.EMOTICONS))
update_exc(TOKENIZER_EXCEPTIONS, strings_to_exc(base.ABBREVIATIONS))


__all__ = ["TOKENIZER_EXCEPTIONS", "TAG_MAP", "STOP_WORDS", "MORPH_RULES",
           "LEMMA_RULES", "LEMMA_INDEX", "LEMMA_EXC"]
