# encoding: utf8
from __future__ import unicode_literals

import six

from spacy.language_data import strings_to_exc, update_exc
from .punctuations import *
from .stop_words import STOP_WORDS
from .tokenizer_exceptions import ABBREVIATIONS
from .tokenizer_exceptions import OTHER_EXC
from .. import language_data as base

STOP_WORDS = set(STOP_WORDS)
TOKENIZER_EXCEPTIONS = strings_to_exc(base.EMOTICONS)
TOKENIZER_PREFIXES = base.TOKENIZER_PREFIXES + TOKENIZER_PREFIXES
TOKENIZER_SUFFIXES = TOKENIZER_SUFFIXES
TOKENIZER_INFIXES = TOKENIZER_INFIXES

# HYPHENS = [six.unichr(cp) for cp in [173, 8211, 8212, 8213, 8722, 9472]]

update_exc(TOKENIZER_EXCEPTIONS, strings_to_exc(OTHER_EXC))
update_exc(TOKENIZER_EXCEPTIONS, strings_to_exc(ABBREVIATIONS))

__all__ = ["TOKENIZER_EXCEPTIONS", "STOP_WORDS", "TOKENIZER_PREFIXES", "TOKENIZER_SUFFIXES", "TOKENIZER_INFIXES"]
