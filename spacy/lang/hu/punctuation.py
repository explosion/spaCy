# coding: utf8
from __future__ import unicode_literals

from ..char_classes import LIST_PUNCT, LIST_ELLIPSES, LIST_QUOTES
from ..char_classes import QUOTES, UNITS, ALPHA, ALPHA_LOWER, ALPHA_UPPER

LIST_ICONS = [r'[\p{So}--[°]]']

_currency = r'\$|¢|£|€|¥|฿'
_quotes = QUOTES.replace("'", '')

_prefixes = ([r'\+'] + LIST_PUNCT + LIST_ELLIPSES + LIST_QUOTES + LIST_ICONS +
             [r'[,.:](?=[{a}])'.format(a=ALPHA)])

_suffixes = (LIST_PUNCT + LIST_ELLIPSES + LIST_QUOTES + LIST_ICONS +
             [r'(?<=[0-9])\+',
              r'(?<=°[FfCcKk])\.',
              r'(?<=[0-9])(?:{})'.format(_currency),
              r'(?<=[0-9])(?:{})'.format(UNITS),
              r'(?<=[{}{}{}(?:{})])\.'.format(ALPHA_LOWER, r'%²\-\)\]\+', QUOTES, _currency),
              r'(?<=[{})])-e'.format(ALPHA_LOWER)])

_infixes = (LIST_ELLIPSES + LIST_ICONS +
            [r'(?<=[{}])\.(?=[{}])'.format(ALPHA_LOWER, ALPHA_UPPER),
             r'(?<=[{a}])[,!?](?=[{a}])'.format(a=ALPHA),
             r'(?<=[{a}"])[:<>=](?=[{a}])'.format(a=ALPHA),
             r'(?<=[{a}])--(?=[{a}])'.format(a=ALPHA),
             r'(?<=[{a}]),(?=[{a}])'.format(a=ALPHA),
             r'(?<=[{a}])([{q}\)\]\(\[])(?=[\-{a}])'.format(a=ALPHA, q=_quotes)])

TOKENIZER_PREFIXES = _prefixes
TOKENIZER_SUFFIXES = _suffixes
TOKENIZER_INFIXES = _infixes
