# coding: utf8
from __future__ import unicode_literals

from ..char_classes import LIST_PUNCT, LIST_ELLIPSES, LIST_QUOTES, LIST_ICONS
from ..char_classes import ALPHA_LOWER, ALPHA_UPPER, ALPHA, HYPHENS, QUOTES, UNITS


_currency = r"\$|¢|£|€|¥|฿|৳"
_quotes = QUOTES.replace("'", '')
_list_punct = LIST_PUNCT + '। ॥'.strip().split()


_prefixes = ([r'\+'] + _list_punct + LIST_ELLIPSES + LIST_QUOTES + LIST_ICONS)

_suffixes = (_list_punct + LIST_ELLIPSES + LIST_QUOTES + LIST_ICONS +
             [r'(?<=[0-9])\+',
              r'(?<=°[FfCcKk])\.',
              r'(?<=[0-9])(?:{})'.format(_currency),
              r'(?<=[0-9])(?:{})'.format(UNITS),
              r'(?<=[{}(?:{})])\.'.format('|'.join([ALPHA_LOWER, r'%²\-\)\]\+', QUOTES]), _currency)])

_infixes = (LIST_ELLIPSES + LIST_ICONS +
            [r'(?<=[0-9{zero}-{nine}])[+\-\*^=](?=[0-9{zero}-{nine}-])'.format(zero=u'০', nine=u'৯'),
             r'(?<=[{a}]),(?=[{a}])'.format(a=ALPHA),
             r'(?<=[{a}])[{h}](?={ae})'.format(a=ALPHA, h=HYPHENS, ae=u'এ'),
             r'(?<=[{a}])[?";:=,.]*(?:{h})(?=[{a}])'.format(a=ALPHA, h=HYPHENS),
             r'(?<=[{a}"])[:<>=/](?=[{a}])'.format(a=ALPHA)])


TOKENIZER_PREFIXES = _prefixes
TOKENIZER_SUFFIXES = _suffixes
TOKENIZER_INFIXES = _infixes
