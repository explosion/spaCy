from ..char_classes import (
    ALPHA,
    ALPHA_LOWER,
    CONCAT_QUOTES,
    HYPHENS,
    LIST_ELLIPSES,
    LIST_ICONS,
    LIST_PUNCT,
    LIST_QUOTES,
    UNITS,
)

_currency = r"\$¢£€¥฿৳"
_quotes = CONCAT_QUOTES.replace("'", "")
_list_punct = LIST_PUNCT + "। ॥".strip().split()


_prefixes = [r"\+"] + _list_punct + LIST_ELLIPSES + LIST_QUOTES + LIST_ICONS

_suffixes = (
    _list_punct
    + LIST_ELLIPSES
    + LIST_QUOTES
    + LIST_ICONS
    + [
        r"(?<=[0-9])\+",
        r"(?<=°[FfCcKk])\.",
        r"(?<=[0-9])(?:[{c}])".format(c=_currency),
        r"(?<=[0-9])(?:{u})".format(u=UNITS),
        r"(?<=[{al}{e}{q}(?:{c})])\.".format(
            al=ALPHA_LOWER, e=r"%²\-\+", q=CONCAT_QUOTES, c=_currency
        ),
    ]
)

_infixes = (
    LIST_ELLIPSES
    + LIST_ICONS
    + [
        r"(?<=[0-9{zero}-{nine}])[+\-\*^=](?=[0-9{zero}-{nine}-])".format(
            zero="০", nine="৯"
        ),
        r"(?<=[{a}]),(?=[{a}])".format(a=ALPHA),
        r"(?<=[{a}])({h})(?=[{ae}])".format(a=ALPHA, h=HYPHENS, ae="এ"),
        r"(?<=[{a}])(?:{h})(?=[{a}])".format(a=ALPHA, h=HYPHENS),
        r"(?<=[{a}])[:<>=/](?=[{a}])".format(a=ALPHA),
    ]
)


TOKENIZER_PREFIXES = _prefixes
TOKENIZER_SUFFIXES = _suffixes
TOKENIZER_INFIXES = _infixes
