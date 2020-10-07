from ..char_classes import LIST_PUNCT, LIST_ELLIPSES, LIST_QUOTES, CURRENCY
from ..char_classes import UNITS, ALPHA_UPPER

_suffixes = (
    LIST_PUNCT
    + LIST_ELLIPSES
    + LIST_QUOTES
    + [
        r"(?<=[0-9])\+",
        # Arabic is written from Right-To-Left
        r"(?<=[0-9])(?:{c})".format(c=CURRENCY),
        r"(?<=[0-9])(?:{u})".format(u=UNITS),
        r"(?<=[{au}][{au}])\.".format(au=ALPHA_UPPER),
    ]
)

TOKENIZER_SUFFIXES = _suffixes
