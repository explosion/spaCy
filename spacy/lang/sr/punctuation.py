from ..char_classes import (
    ALPHA,
    ALPHA_LOWER,
    ALPHA_UPPER,
    CONCAT_QUOTES,
    CURRENCY,
    LIST_ELLIPSES,
    LIST_ICONS,
    LIST_PUNCT,
    LIST_QUOTES,
    PUNCT,
    UNITS,
)

_infixes = (
    LIST_ELLIPSES
    + LIST_ICONS
    + [
        r"(?<=[0-9])[+\-\*^](?=[0-9-])",
        r"(?<=[{al}{q}])\.(?=[{au}{q}])".format(
            al=ALPHA_LOWER, au=ALPHA_UPPER, q=CONCAT_QUOTES
        ),
        r"(?<=[{a}]),(?=[{a}])".format(a=ALPHA),
        r"(?<=[{a}0-9])[:<>=/](?=[{a}])".format(a=ALPHA),
    ]
)

_suffixes = (
    LIST_PUNCT
    + LIST_ELLIPSES
    + LIST_QUOTES
    + LIST_ICONS
    + [
        r"(?<=[0-9])\+",
        r"(?<=°[FfCcKk])\.",
        r"(?<=[0-9])(?:{c})".format(c=CURRENCY),
        r"(?<=[0-9])(?:{u})".format(u=UNITS),
        r"(?<=[{a}{e}{p}(?:{q})])\.".format(
            a=ALPHA, e=r"%²\-\+", q=CONCAT_QUOTES, p=PUNCT
        ),
    ]
)

TOKENIZER_INFIXES = _infixes
TOKENIZER_SUFFIXES = _suffixes
