# coding: utf8
from __future__ import unicode_literals



CURRENCY_SYMBOLS = r"\$ ¢ £ € ¥ ฿ ৳"

_PUNCT = '। ॥'

LIST_PUNCT.extend(_PUNCT.strip().split())

TOKENIZER_PREFIXES = (
    [r'\+'] +
    LIST_PUNCT +
    LIST_ELLIPSES +
    LIST_QUOTES
)

TOKENIZER_SUFFIXES = (
    LIST_PUNCT +
    LIST_ELLIPSES +
    LIST_QUOTES +
    [
        r'(?<=[0-9])\+',
        r'(?<=°[FfCcKk])\.',
        r'(?<=[0-9])(?:{c})'.format(c=CURRENCY),
        r'(?<=[0-9])(?:{u})'.format(u=UNITS),
        r'(?<=[{al}{p}{c}(?:{q})])\.'.format(al=ALPHA_LOWER, p=r'%²\-\)\]\+', q=QUOTES, c=CURRENCY_SYMBOLS),
        r'(?<=[{al})])-e'.format(al=ALPHA_LOWER)
    ]
)

TOKENIZER_INFIXES = (
    LIST_ELLIPSES +
    [
        r'(?<=[{al}])\.(?=[{au}])'.format(al=ALPHA_LOWER, au=ALPHA_UPPER),
        r'(?<=[{a}]),(?=[{a}])'.format(a=ALPHA),
        r'(?<=[{a}"])[:<>=](?=[{a}])'.format(a=ALPHA),
        r'(?<=[{a}])--(?=[{a}])'.format(a=ALPHA),
        r'(?<=[{a}]),(?=[{a}])'.format(a=ALPHA),
        r'(?<=[{a}])([{q}\)\]\(\[])(?=[\-{a}])'.format(a=ALPHA, q=_QUOTES.replace("'", "").strip().replace(" ", "")),
    ]
)
from ..char_classes import LIST_PUNCT, LIST_ELLIPSES, LIST_QUOTES, UNITS
from ..char_classes import ALPHA_LOWER, ALPHA_UPPER, ALPHA, HYPHENS, QUOTES
