# coding: utf8
from __future__ import unicode_literals

from ..char_classes import LIST_ELLIPSES, LIST_ICONS, LIST_PUNCT, LIST_QUOTES
from ..char_classes import LIST_CURRENCY, CURRENCY, UNITS, PUNCT
from ..char_classes import CONCAT_QUOTES, ALPHA, ALPHA_LOWER, ALPHA_UPPER
from ..punctuation import _prefixes, _suffixes


_prefixes = ["``",] + list(_prefixes)

_suffixes = (
    ["''", "/"]
    + LIST_PUNCT
    + LIST_ELLIPSES
    + LIST_QUOTES
    + LIST_ICONS
    + [
        r"(?<=[0-9])\+",
        r"(?<=°[FfCcKk])\.",
        r"(?<=[0-9])(?:{c})".format(c=CURRENCY),
        r"(?<=[0-9])(?:{u})".format(u=UNITS),
        r"(?<=[{al}{e}{p}(?:{q})])\.".format(
            al=ALPHA_LOWER, e=r"%²\-\+", q=CONCAT_QUOTES, p=PUNCT
        ),
        r"(?<=[{au}][{au}])\.".format(au=ALPHA_UPPER),
    ]
)

_quotes = CONCAT_QUOTES.replace("'", "")

_infixes = (
    LIST_ELLIPSES
    + LIST_ICONS
    + [
        r"(?<=[{al}])\.(?=[{au}])".format(al=ALPHA_LOWER, au=ALPHA_UPPER),
        r"(?<=[{a}])[,!?](?=[{a}])".format(a=ALPHA),
        r"(?<=[{a}])[:<>=](?=[{a}])".format(a=ALPHA),
        r"(?<=[{a}]),(?=[{a}])".format(a=ALPHA),
        r"(?<=[0-9{a}])\/(?=[0-9{a}])".format(a=ALPHA),
        r"(?<=[{a}])([{q}\)\]\(\[])(?=[{a}])".format(a=ALPHA, q=_quotes),
        r"(?<=[{a}])--(?=[{a}])".format(a=ALPHA),
        r"(?<=[0-9])-(?=[0-9])",
    ]
)


TOKENIZER_PREFIXES = _prefixes
TOKENIZER_SUFFIXES = _suffixes
TOKENIZER_INFIXES = _infixes
