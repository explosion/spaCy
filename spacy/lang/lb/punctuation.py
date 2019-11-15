# coding: utf8
from __future__ import unicode_literals

from ..punctuation import TOKENIZER_INFIXES
from ..char_classes import ALPHA


ELISION = " ' ’ ".strip().replace(" ", "").replace("\n", "")
HYPHENS = r"- – — ‐ ‑".strip().replace(" ", "").replace("\n", "")


_infixes = TOKENIZER_INFIXES + [
    r"(?<=[{a}][{el}])(?=[{a}])".format(a=ALPHA, el=ELISION)
]

TOKENIZER_INFIXES = _infixes
