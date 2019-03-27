# coding: utf8
from __future__ import unicode_literals

from ..punctuation import TOKENIZER_INFIXES
from ..char_classes import LIST_PUNCT, LIST_ELLIPSES, LIST_QUOTES, CURRENCY
from ..char_classes import CONCAT_QUOTES, UNITS, ALPHA, ALPHA_LOWER, ALPHA_UPPER


ELISION = " ' ’ ".strip().replace(" ", "").replace("\n", "")
HYPHENS = r"- – — ‐ ‑".strip().replace(" ", "").replace("\n", "")


_suffixes = (
    LIST_PUNCT
    + LIST_ELLIPSES
    + LIST_QUOTES
    + [
        r"(?<=[0-9])\+",
        r"(?<=°[FfCcKk])\.",  # °C. -> ["°C", "."]
        r"(?<=[0-9])°[FfCcKk]",  # 4°C -> ["4", "°C"]
        r"(?<=[0-9])%",  # 4% -> ["4", "%"]
        r"(?<=[0-9])(?:{c})".format(c=CURRENCY),
        r"(?<=[0-9])(?:{u})".format(u=UNITS),
        r"(?<=[0-9{al}{e}(?:{q})])\.".format(
            al=ALPHA_LOWER, e=r"%²\-\+", q=CONCAT_QUOTES
        ),
        r"(?<=[{au}][{au}])\.".format(au=ALPHA_UPPER),
    ]
)


_infixes = TOKENIZER_INFIXES + [
    r"(?<=[{a}][{el}])(?=[{a}])".format(a=ALPHA, el=ELISION)
]


TOKENIZER_SUFFIXES = _suffixes
TOKENIZER_INFIXES = _infixes
