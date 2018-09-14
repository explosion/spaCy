# coding: utf8
from __future__ import unicode_literals

from ..punctuation import TOKENIZER_PREFIXES, TOKENIZER_SUFFIXES, TOKENIZER_INFIXES
from ..char_classes import merge_chars, split_chars, _currency, _units
from ..char_classes import LIST_PUNCT, LIST_ELLIPSES, LIST_QUOTES
from ..char_classes import QUOTES, ALPHA, ALPHA_LOWER, ALPHA_UPPER, HYPHENS

_units = (_units + 's bit Gbps Mbps mbps Kbps kbps ƒ ppi px '
          'Hz kHz MHz GHz mAh '
          'ratus rb ribu ribuan '
          'juta jt jutaan mill?iar million bil[l]?iun bilyun billion '
          )
_currency = (_currency + r' USD Rp IDR RMB SGD S\$')
_months = ('Januari Februari Maret April Mei Juni Juli Agustus September '
           'Oktober November Desember January February March May June '
           'July August October December Jan Feb Mar Jun Jul Aug Sept '
           'Oct Okt Nov Des ')


UNITS = merge_chars(_units)
CURRENCY = merge_chars(_currency)
HTML_PREFIX = r'<(b|strong|i|em|p|span|div|br)\s?/>|<a([^>]+)>'
HTML_SUFFIX = r'</(b|strong|i|em|p|span|div|a)>'
MONTHS = merge_chars(_months)
LIST_CURRENCY = split_chars(_currency)

TOKENIZER_PREFIXES.remove('#')  # hashtag
_prefixes = TOKENIZER_PREFIXES + LIST_CURRENCY + [HTML_PREFIX] + ['/', '—']

_suffixes = TOKENIZER_SUFFIXES + [r'\-[Nn]ya', '-[KkMm]u', '[—-]'] + [
        r'(?<={c})(?:[0-9]+)'.format(c=CURRENCY),
        r'(?<=[0-9])(?:{u})'.format(u=UNITS),
        r'(?<=[0-9])%',
        r'(?<=[0-9{a}]{h})(?:[\.,:-])'.format(a=ALPHA, h=HTML_SUFFIX),
        r'(?<=[0-9{a}])(?:{h})'.format(a=ALPHA, h=HTML_SUFFIX),
    ]

_infixes = TOKENIZER_INFIXES + [
    r'(?<=[0-9])[\\/](?=[0-9%-])',
    r'(?<=[0-9])%(?=[{a}0-9/])'.format(a=ALPHA),
    r'(?<={u})[\/-](?=[0-9])'.format(u=UNITS),
    r'(?<={m})[\/-](?=[0-9])'.format(m=MONTHS),
    r'(?<=[0-9\)][\.,])"(?=[0-9])',
    r'(?<=[{a}\)][\.,\'])["—](?=[{a}])'.format(a=ALPHA),
    r'(?<=[{a}])-(?=[0-9])'.format(a=ALPHA),
    r'(?<=[0-9])-(?=[{a}])'.format(a=ALPHA),
    r'(?<=[{a}])[\/-](?={c}{a})'.format(a=ALPHA, c=CURRENCY),
]

TOKENIZER_PREFIXES = _prefixes
TOKENIZER_SUFFIXES = _suffixes
TOKENIZER_INFIXES = _infixes
