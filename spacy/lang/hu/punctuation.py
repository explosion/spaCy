# coding: utf8
from __future__ import unicode_literals

from ..char_classes import LIST_PUNCT, LIST_ELLIPSES, LIST_QUOTES, CONCAT_QUOTES
from ..char_classes import CONCAT_ICONS, ALPHA, ALPHA_LOWER, ALPHA_UPPER
from ..char_classes import LIST_UNITS, merge_chars


# removing ° from the special icons to keep e.g. 99° as one token
_concat_icons = CONCAT_ICONS.replace("\u00B0", "")

_currency = r"\$¢£€¥฿"
_quotes = CONCAT_QUOTES.replace("'", "")
_list_units = [s for s in LIST_UNITS if s != "%"]
_units = merge_chars(" ".join(_list_units))

_prefixes = (
    LIST_PUNCT
    + LIST_ELLIPSES
    + LIST_QUOTES
    + [_concat_icons]
    + [r"[,.:](?=[{a}])".format(a=ALPHA)]
)

_suffixes = (
    LIST_PUNCT
    + LIST_ELLIPSES
    + LIST_QUOTES
    + [_concat_icons]
    + [
        r"(?<=[0-9])\+",
        r"(?<=°[FfCcKk])\.",
        r"(?<=[0-9])(?:[{c}])".format(c=_currency),
        r"(?<=[0-9])(?:{u})".format(u=_units),
        r"(?<=[{al}{e}{q}(?:{c})])\.".format(
            al=ALPHA_LOWER, e=r"%²\-\+", q=CONCAT_QUOTES, c=_currency
        ),
        r"(?<=[{al})])-e".format(al=ALPHA_LOWER),
    ]
)

_infixes = (
    LIST_ELLIPSES
    + [_concat_icons]
    + [
        r"(?<=[{al}])\.(?=[{au}])".format(al=ALPHA_LOWER, au=ALPHA_UPPER),
        r"(?<=[{a}])[,!?](?=[{a}])".format(a=ALPHA),
        r"(?<=[{a}])[:<>=](?=[{a}])".format(a=ALPHA),
        r"(?<=[{a}])--(?=[{a}])".format(a=ALPHA),
        r"(?<=[{a}]),(?=[{a}])".format(a=ALPHA),
        r"(?<=[{a}])([{q}\)\]\(\[])(?=[\-{a}])".format(a=ALPHA, q=_quotes),
    ]
)

TOKENIZER_PREFIXES = _prefixes
TOKENIZER_SUFFIXES = _suffixes
TOKENIZER_INFIXES = _infixes
