from ..char_classes import (
    ALPHA_UPPER,
    CURRENCY,
    LIST_ELLIPSES,
    LIST_PUNCT,
    LIST_QUOTES,
    UNITS,
)

_suffixes = (
    LIST_PUNCT
    + LIST_ELLIPSES
    + LIST_QUOTES
    + [
        r"(?<=[0-9])\+",
        r"(?<=[0-9])%",  # 4% -> ["4", "%"]
        # Persian is written from Right-To-Left
        r"(?<=[0-9])(?:{c})".format(c=CURRENCY),
        r"(?<=[0-9])(?:{u})".format(u=UNITS),
        r"(?<=[{au}][{au}])\.".format(au=ALPHA_UPPER),
    ]
)

TOKENIZER_SUFFIXES = _suffixes
