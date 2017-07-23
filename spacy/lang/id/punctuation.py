# coding: utf8
from __future__ import unicode_literals

from ..punctuation import TOKENIZER_PREFIXES, TOKENIZER_SUFFIXES, TOKENIZER_INFIXES
from ..char_classes import merge_chars, split_chars, _currency
from ..char_classes import LIST_PUNCT, LIST_ELLIPSES, LIST_QUOTES
from ..char_classes import QUOTES, UNITS, ALPHA, ALPHA_LOWER, ALPHA_UPPER

_units = ('s bit Gbps Mbps mbps Kbps kbps ƒ '
          'kHz MHz GHz mAh ')
_currency = r'Rp IDR RMB SGD S\$' + _currency

UNITS = merge_chars(_units)
CURRENCY = merge_chars(_currency)
HTML_PREFIX = r'<(b|strong|i|em|p|span|div|br)\s?/>'
HTML_SUFFIX = r'</(b|strong|i|em|p|span|div)>'

_prefixes = TOKENIZER_PREFIXES + split_chars(_currency) + [HTML_PREFIX] + ['ke-']

_suffixes = TOKENIZER_SUFFIXES + [
        r'(?<=[0-9])(?:{})'.format(CURRENCY),
        r'(?<=[0-9])(?:{})'.format(UNITS),
        r'(?<=[0-9])%',
        r'(?<=[0-9{a}]{h})(?:[\.,:-])'.format(a=ALPHA, h=HTML_SUFFIX),
        r'(?<=[0-9{a}])(?:{h})'.format(a=ALPHA, h=HTML_SUFFIX),
    ]

_infixes = TOKENIZER_INFIXES + [
    r'(?<=[0-9])([\\/])(?=[0-9%-])',
    r'(?<=[0-9])(%)(?=[{a}0-9/])'.format(a=ALPHA),
    r'(?<=[0-9]{u})\/(?=[0-9])'.format(u=UNITS),
]

TOKENIZER_PREFIXES = _prefixes
TOKENIZER_SUFFIXES = _suffixes
TOKENIZER_INFIXES = _infixes
