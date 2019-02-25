# coding: utf8
from __future__ import unicode_literals
from ..char_classes import LIST_ELLIPSES, LIST_ICONS
from ..char_classes import QUOTES, ALPHA, ALPHA_LOWER, ALPHA_UPPER
_quotes = QUOTES.replace("'", '')
_infixes = (LIST_ELLIPSES + LIST_ICONS +
            [r'(?<=[{}])\.(?=[{}])'.format(ALPHA_LOWER, ALPHA_UPPER),
             r'(?<=[{a}])[,!?](?=[{a}])'.format(a=ALPHA),
             r'(?<=[{a}"])[:<>=](?=[{a}])'.format(a=ALPHA),
             r'(?<=[{a}]),(?=[{a}])'.format(a=ALPHA),
             r'(?<=[{a}])([{q}\)\]\(\[])(?=[\{a}])'.format(a=ALPHA, q=_quotes),
             r'(?<=[{a}])--(?=[{a}])'.format(a=ALPHA)])

TOKENIZER_INFIXES = _infixes
