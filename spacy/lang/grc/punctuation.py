from ..char_classes import (
    ALPHA,
    ALPHA_LOWER,
    ALPHA_UPPER,
    CONCAT_QUOTES,
    HYPHENS,
    LIST_CURRENCY,
    LIST_ELLIPSES,
    LIST_ICONS,
    LIST_PUNCT,
    LIST_QUOTES,
)

_prefixes = (
    [
        "†",
        "⸏",
    ]
    + LIST_PUNCT
    + LIST_ELLIPSES
    + LIST_QUOTES
    + LIST_CURRENCY
    + LIST_ICONS
)

_suffixes = (
    LIST_PUNCT
    + LIST_ELLIPSES
    + LIST_QUOTES
    + LIST_ICONS
    + [
        "†",
        "⸎",
        r"(?<=[\u1F00-\u1FFF\u0370-\u03FF])[\-\.⸏]",
    ]
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
        r"(?<=[{a}0-9])(?:{h})(?=[{a}])".format(a=ALPHA, h=HYPHENS),
        r"(?<=[{a}0-9])[:<>=/](?=[{a}])".format(a=ALPHA),
        r"(?<=[\u1F00-\u1FFF\u0370-\u03FF])—",
    ]
)

TOKENIZER_PREFIXES = _prefixes
TOKENIZER_SUFFIXES = _suffixes
TOKENIZER_INFIXES = _infixes
