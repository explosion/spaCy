from ..char_classes import (
    ALPHA,
    ALPHA_LOWER,
    ALPHA_UPPER,
    CONCAT_QUOTES,
    CURRENCY,
    LIST_CURRENCY,
    LIST_ELLIPSES,
    LIST_ICONS,
    LIST_PUNCT,
    LIST_QUOTES,
    PUNCT,
    UNITS,
)

# Punctuation adapted from Danish
_quotes = CONCAT_QUOTES.replace("'", "")
_list_punct = [x for x in LIST_PUNCT if x != "#"]
_list_icons = [x for x in LIST_ICONS if x != "°"]
_list_icons = [x.replace("\\u00B0", "") for x in _list_icons]
_list_quotes = [x for x in LIST_QUOTES if x != "\\'"]


_prefixes = (
    ["§", "%", "=", "—", "–", r"\+(?![0-9])"]
    + _list_punct
    + LIST_ELLIPSES
    + LIST_QUOTES
    + LIST_CURRENCY
    + LIST_ICONS
)


_infixes = (
    LIST_ELLIPSES
    + _list_icons
    + [
        r"(?<=[{al}])\.(?=[{au}])".format(al=ALPHA_LOWER, au=ALPHA_UPPER),
        r"(?<=[{a}])[,!?](?=[{a}])".format(a=ALPHA),
        r"(?<=[{a}])[:<>=/](?=[{a}])".format(a=ALPHA),
        r"(?<=[{a}]),(?=[{a}])".format(a=ALPHA),
        r"(?<=[{a}])([{q}\)\]\(\[])(?=[{a}])".format(a=ALPHA, q=_quotes),
        r"(?<=[{a}])--(?=[{a}])".format(a=ALPHA),
    ]
)

_suffixes = (
    LIST_PUNCT
    + LIST_ELLIPSES
    + _list_quotes
    + _list_icons
    + ["—", "–"]
    + [
        r"(?<=[0-9])\+",
        r"(?<=°[FfCcKk])\.",
        r"(?<=[0-9])(?:{c})".format(c=CURRENCY),
        r"(?<=[0-9])(?:{u})".format(u=UNITS),
        r"(?<=[{al}{e}{p}(?:{q})])\.".format(
            al=ALPHA_LOWER, e=r"%²\-\+", q=_quotes, p=PUNCT
        ),
        r"(?<=[{au}][{au}])\.".format(au=ALPHA_UPPER),
    ]
    + [r"(?<=[^sSxXzZ])'"]
)


TOKENIZER_PREFIXES = _prefixes
TOKENIZER_INFIXES = _infixes
TOKENIZER_SUFFIXES = _suffixes
