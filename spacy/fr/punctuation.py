# coding: utf8
from __future__ import unicode_literals

from ..language_data.punctuation import ALPHA, TOKENIZER_INFIXES, LIST_PUNCT
from ..language_data.punctuation import LIST_ELLIPSES, LIST_QUOTES, CURRENCY
from ..language_data.punctuation import UNITS, ALPHA_LOWER, QUOTES, ALPHA_UPPER


ELISION = " ' ’ ".strip().replace(' ', '').replace('\n', '')
HYPHENS = r"""- – — ‐ ‑""".strip().replace(' ', '').replace('\n', '')


TOKENIZER_SUFFIXES = (
    LIST_PUNCT +
    LIST_ELLIPSES +
    LIST_QUOTES +
    [
        r'(?<=[0-9])\+',
        r'(?<=°[FfCcKk])\.',  # 4°C. -> ["4°C", "."]
        r'(?<=[0-9])°[FfCcKk]',  # 4°C -> ["4", "°C"]
        r'(?<=[0-9])%',  # 4% -> ["4", "%"]
        r'(?<=[0-9])(?:{c})'.format(c=CURRENCY),
        r'(?<=[0-9])(?:{u})'.format(u=UNITS),
        r'(?<=[0-9{al}{p}(?:{q})])\.'.format(al=ALPHA_LOWER, p=r'%²\-\)\]\+', q=QUOTES),
        r'(?<=[{au}][{au}])\.'.format(au=ALPHA_UPPER)])


TOKENIZER_INFIXES += [
    r'(?<=[{a}][{el}])(?=[{a}])'.format(a=ALPHA, el=ELISION)]
