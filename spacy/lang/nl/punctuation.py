# coding: utf8
from __future__ import unicode_literals

from ..char_classes import LIST_ELLIPSES, LIST_ICONS, LIST_UNITS, merge_chars
from ..char_classes import LIST_PUNCT, LIST_QUOTES, CURRENCY, PUNCT
from ..char_classes import CONCAT_QUOTES, ALPHA, ALPHA_LOWER, ALPHA_UPPER

from ..punctuation import TOKENIZER_PREFIXES as BASE_TOKENIZER_PREFIXES


_prefixes = [",,"] + BASE_TOKENIZER_PREFIXES


# Copied from `de` package. Main purpose is to ensure that hyphens are not
# split on.

_quotes = CONCAT_QUOTES.replace("'", "")

_infixes = (
    LIST_ELLIPSES
    + LIST_ICONS
    + [
        r"(?<=[{}])\.(?=[{}])".format(ALPHA_LOWER, ALPHA_UPPER),
        r"(?<=[{a}])[,!?](?=[{a}])".format(a=ALPHA),
        r'(?<=[{a}"])[:<>=](?=[{a}])'.format(a=ALPHA),
        r"(?<=[{a}]),(?=[{a}])".format(a=ALPHA),
        r"(?<=[{a}])([{q}\)\]\(\[])(?=[{a}])".format(a=ALPHA, q=_quotes),
        r"(?<=[{a}])--(?=[{a}])".format(a=ALPHA),
    ]
)


_list_units = [u for u in LIST_UNITS if u != "%"]
_units = merge_chars(" ".join(_list_units))

_suffixes = (
    ["''"]
    + LIST_PUNCT
    + LIST_ELLIPSES
    + LIST_QUOTES
    + LIST_ICONS
    + ["—", "–"]
    + [
        r"(?<=[0-9])\+",
        r"(?<=°[FfCcKk])\.",
        r"(?<=[0-9])(?:{c})".format(c=CURRENCY),
        r"(?<=[0-9])(?:{u})".format(u=_units),
        r"(?<=[0-9{al}{e}{p}(?:{q})])\.".format(
            al=ALPHA_LOWER, e=r"%²\-\+", q=CONCAT_QUOTES, p=PUNCT
        ),
        r"(?<=[{au}][{au}])\.".format(au=ALPHA_UPPER),
    ]
)


TOKENIZER_PREFIXES = _prefixes
TOKENIZER_INFIXES = _infixes
TOKENIZER_SUFFIXES = _suffixes
