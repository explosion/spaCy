# coding: utf8
from __future__ import unicode_literals

from ..punctuation import TOKENIZER_INFIXES
from ..char_classes import LIST_PUNCT, LIST_ELLIPSES, LIST_QUOTES, CURRENCY
from ..char_classes import QUOTES, UNITS, ALPHA, ALPHA_LOWER, ALPHA_UPPER

_suffixes = (LIST_PUNCT + LIST_ELLIPSES + LIST_QUOTES +
             [r'(?<=[0-9])\+',
              # Arabic is written from Right-To-Left
              r'(?<=[0-9])(?:{})'.format(CURRENCY),
              r'(?<=[0-9])(?:{})'.format(UNITS),
              r'(?<=[{au}][{au}])\.'.format(au=ALPHA_UPPER)])

TOKENIZER_SUFFIXES = _suffixes
