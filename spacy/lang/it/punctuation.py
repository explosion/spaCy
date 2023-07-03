from ..char_classes import (
    ALPHA,
    ALPHA_LOWER,
    ALPHA_UPPER,
    CONCAT_QUOTES,
    HYPHENS,
    LIST_ELLIPSES,
    LIST_ICONS,
)
from ..punctuation import TOKENIZER_PREFIXES as BASE_TOKENIZER_PREFIXES

ELISION = "'’"


_prefixes = [r"'[0-9][0-9]", r"[0-9]+°"] + BASE_TOKENIZER_PREFIXES


_infixes = (
    LIST_ELLIPSES
    + LIST_ICONS
    + [
        r"(?<=[0-9])[+\-\*^](?=[0-9-])",
        r"(?<=[{al}{q}])\.(?=[{au}{q}])".format(
            al=ALPHA_LOWER, au=ALPHA_UPPER, q=CONCAT_QUOTES
        ),
        r"(?<=[{a}]),(?=[{a}])".format(a=ALPHA),
        r"(?<=[{a}])(?:{h})(?=[{al}])".format(a=ALPHA, h=HYPHENS, al=ALPHA_LOWER),
        r"(?<=[{a}0-9])[:<>=\/](?=[{a}])".format(a=ALPHA),
        r"(?<=[{a}][{el}])(?=[{a}0-9\"])".format(a=ALPHA, el=ELISION),
    ]
)

TOKENIZER_PREFIXES = _prefixes
TOKENIZER_INFIXES = _infixes
