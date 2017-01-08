# encoding: utf8
from __future__ import unicode_literals

from ..language_data.punctuation import ALPHA, ALPHA_LOWER, ALPHA_UPPER, LIST_ELLIPSES


TOKENIZER_SUFFIXES = [
    r'(?<=[{al})])-e'.format(al=ALPHA_LOWER)
]

TOKENIZER_INFIXES = [
    r'(?<=[0-9])-(?=[0-9])',
    r'(?<=[0-9])[+\-\*/^](?=[0-9])',
    r'(?<=[{a}])--(?=[{a}])',
    r'(?<=[{a}]),(?=[{a}])'.format(a=ALPHA),
    r'(?<=[{al}])\.(?=[{au}])'.format(al=ALPHA_LOWER, au=ALPHA_UPPER),
    r'(?<=[0-9{a}])"(?=[\-{a}])'.format(a=ALPHA),
    r'(?<=[{a}"])[:<>=](?=[{a}])'.format(a=ALPHA)
]


TOKENIZER_INFIXES += LIST_ELLIPSES


__all__ = ["TOKENIZER_SUFFIXES", "TOKENIZER_INFIXES"]
