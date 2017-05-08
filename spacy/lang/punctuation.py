# coding: utf8
from __future__ import unicode_literals

from .char_classes import LIST_PUNCT, LIST_ELLIPSES, LIST_QUOTES, LIST_CURRENCY
from .char_classes import ALPHA_LOWER, ALPHA_UPPER, ALPHA, HYPHENS, QUOTES
from .char_classes import CURRENCY, UNITS


_prefixes = (['§', '%', '=', r'\+'] + LIST_PUNCT + LIST_ELLIPSES + LIST_QUOTES +
             LIST_CURRENCY)


_suffixes = (["'s", "'S", "’s", "’S"] + LIST_PUNCT + LIST_ELLIPSES + LIST_QUOTES +
             [r'(?<=[0-9])\+',
              r'(?<=°[FfCcKk])\.',
              r'(?<=[0-9])(?:{})'.format(CURRENCY),
              r'(?<=[0-9])(?:{})'.format(UNITS),
              r'(?<=[0-9{}{}(?:{})])\.'.format(ALPHA_LOWER, r'%²\-\)\]\+', QUOTES),
              r'(?<=[{a}][{a}])\.'.format(a=ALPHA_UPPER)])


_infixes = (LIST_ELLIPSES +
            [r'(?<=[0-9])[+\-\*^](?=[0-9-])',
             r'(?<=[{}])\.(?=[{}])'.format(ALPHA_LOWER, ALPHA_UPPER),
             r'(?<=[{a}]),(?=[{a}])'.format(a=ALPHA),
             r'(?<=[{a}])[?";:=,.]*(?:{h})(?=[{a}])'.format(a=ALPHA, h=HYPHENS),
             r'(?<=[{a}"])[:<>=/](?=[{a}])'.format(a=ALPHA)])


TOKENIZER_PREFIXES = _prefixes
TOKENIZER_SUFFIXES = _suffixes
TOKENIZER_INFIXES = _infixes
