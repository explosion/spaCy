# coding: utf8
from __future__ import unicode_literals

from ..language_data.punctuation import ALPHA_LOWER, LIST_ELLIPSES, QUOTES
from ..language_data.punctuation import ALPHA_UPPER, LIST_QUOTES, UNITS
from ..language_data.punctuation import CURRENCY, LIST_PUNCT, ALPHA, _QUOTES


_currency_symbols = r"\$ ¢ £ € ¥ ฿"


TOKENIZER_PREFIXES = (
    [r'\+'] +
    LIST_PUNCT +
    LIST_ELLIPSES +
    LIST_QUOTES)


TOKENIZER_SUFFIXES = (
    LIST_PUNCT +
    LIST_ELLIPSES +
    LIST_QUOTES +
    [
        r'(?<=[0-9])\+',
        r'(?<=°[FfCcKk])\.',
        r'(?<=[0-9])(?:{c})'.format(c=CURRENCY),
        r'(?<=[0-9])(?:{u})'.format(u=UNITS),
        r'(?<=[{al}{p}{c}(?:{q})])\.'.format(al=ALPHA_LOWER, p=r'%²\-\)\]\+', q=QUOTES, c=_currency_symbols),
        r'(?<=[{al})])-e'.format(al=ALPHA_LOWER)])


TOKENIZER_INFIXES = (
    LIST_ELLIPSES +
    [
        r'(?<=[{al}])\.(?=[{au}])'.format(al=ALPHA_LOWER, au=ALPHA_UPPER),
        r'(?<=[{a}]),(?=[{a}])'.format(a=ALPHA),
        r'(?<=[{a}"])[:<>=](?=[{a}])'.format(a=ALPHA),
        r'(?<=[{a}])--(?=[{a}])'.format(a=ALPHA),
        r'(?<=[{a}]),(?=[{a}])'.format(a=ALPHA),
        r'(?<=[{a}])([{q}\)\]\(\[])(?=[\-{a}])'.format(a=ALPHA, q=_QUOTES.replace("'", "").strip().replace(" ", ""))])
