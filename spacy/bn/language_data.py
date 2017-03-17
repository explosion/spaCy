# coding: utf8
from __future__ import unicode_literals

from spacy.language_data import strings_to_exc, update_exc
from .punctuation import *
from .stop_words import STOP_WORDS
from .tag_map import TAG_MAP as TAG_MAP_BN
from .morph_rules import MORPH_RULES
from .lemma_rules import LEMMA_RULES
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS as TOKENIZER_EXCEPTIONS_BN
from .. import language_data as base

STOP_WORDS = set(STOP_WORDS)

TAG_MAP = base.TAG_MAP
TAG_MAP.update(TAG_MAP_BN)

TOKENIZER_EXCEPTIONS = strings_to_exc(base.EMOTICONS)
update_exc(TOKENIZER_EXCEPTIONS, strings_to_exc(base.ABBREVIATIONS))
TOKENIZER_EXCEPTIONS.update(TOKENIZER_EXCEPTIONS_BN)

TOKENIZER_PREFIXES = TOKENIZER_PREFIXES
TOKENIZER_SUFFIXES = TOKENIZER_SUFFIXES
TOKENIZER_INFIXES = TOKENIZER_INFIXES

__all__ = ["TOKENIZER_EXCEPTIONS", "STOP_WORDS", "TAG_MAP", "MORPH_RULES", "LEMMA_RULES",
           "TOKENIZER_PREFIXES", "TOKENIZER_SUFFIXES", "TOKENIZER_INFIXES"]
