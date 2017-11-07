# coding: utf8
from __future__ import unicode_literals

from .char_classes import LIST_PUNCT, LIST_ELLIPSES, LIST_QUOTES, LIST_CURRENCY
from .char_classes import LIST_ICONS, ALPHA_LOWER, ALPHA_UPPER, ALPHA, HYPHENS
from .char_classes import QUOTES, CURRENCY, UNITS


_prefixes = (['§', '%', '=', r'\+'] + LIST_PUNCT + LIST_ELLIPSES + LIST_QUOTES +
             LIST_CURRENCY + LIST_ICONS)


_suffixes = (LIST_PUNCT + LIST_ELLIPSES + LIST_QUOTES + LIST_ICONS +
             ["'s", "'S", "’s", "’S"] +
             [r'(?<=[0-9])\+',
              r'(?<=°[FfCcKk])\.',
              r'(?<=[0-9])(?:{})'.format(CURRENCY),
              r'(?<=[0-9])(?:{})'.format(UNITS),
              r'(?<=[0-9{}{}(?:{})])\.'.format(ALPHA_LOWER, r'%²\-\)\]\+', QUOTES),
              r'(?<=[{a}][{a}])\.'.format(a=ALPHA_UPPER)])


_infixes = (LIST_ELLIPSES + LIST_ICONS +
            [r'(?<=[0-9])[+\-\*^](?=[0-9-])',
             r'(?<=[{}])\.(?=[{}])'.format(ALPHA_LOWER, ALPHA_UPPER),
             r'(?<=[{a}]),(?=[{a}])'.format(a=ALPHA),
             r'(?<=[{a}])[?";:=,.]*(?:{h})(?=[{a}])'.format(a=ALPHA, h=HYPHENS),
             r'(?<=[{a}"])[:<>=/](?=[{a}])'.format(a=ALPHA)])


TOKENIZER_PREFIXES = _prefixes
TOKENIZER_SUFFIXES = _suffixes
TOKENIZER_INFIXES = _infixes
