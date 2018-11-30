# coding: utf8
from __future__ import unicode_literals

from ..punctuation import TOKENIZER_PREFIXES as BASE_TOKENIZER_PREFIXES
from ..punctuation import TOKENIZER_SUFFIXES as BASE_TOKENIZER_SUFFIXES
from ..punctuation import TOKENIZER_INFIXES as BASE_TOKENIZER_INFIXES

_prefixes = [r"\w{1,3}\$"] + BASE_TOKENIZER_PREFIXES

_suffixes = BASE_TOKENIZER_SUFFIXES

_infixes = [r"(\w+-\w+(-\w+)*)"] + BASE_TOKENIZER_INFIXES

TOKENIZER_PREFIXES = _prefixes
TOKENIZER_SUFFIXES = _suffixes
TOKENIZER_INFIXES = _infixes
