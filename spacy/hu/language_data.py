# encoding: utf8
from __future__ import unicode_literals

from spacy.language_data import strings_to_exc, update_exc
from .punctuation import *
from .stop_words import STOP_WORDS
from .tokenizer_exceptions import ABBREVIATIONS
from .tokenizer_exceptions import OTHER_EXC
from .. import language_data as base

STOP_WORDS = set(STOP_WORDS)

TOKENIZER_EXCEPTIONS = strings_to_exc(base.EMOTICONS)
update_exc(TOKENIZER_EXCEPTIONS, strings_to_exc(base.ABBREVIATIONS))
update_exc(TOKENIZER_EXCEPTIONS, strings_to_exc(OTHER_EXC))
update_exc(TOKENIZER_EXCEPTIONS, strings_to_exc(ABBREVIATIONS))

TOKENIZER_PREFIXES = TOKENIZER_PREFIXES
TOKENIZER_SUFFIXES = TOKENIZER_SUFFIXES
TOKENIZER_INFIXES = TOKENIZER_INFIXES

__all__ = ["TOKENIZER_EXCEPTIONS", "STOP_WORDS", "TOKENIZER_PREFIXES", "TOKENIZER_SUFFIXES", "TOKENIZER_INFIXES"]
