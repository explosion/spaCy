# coding: utf8
from __future__ import unicode_literals

from ..char_classes import LIST_ELLIPSES, LIST_ICONS, ALPHA, ALPHA_LOWER, ALPHA_UPPER

ELISION = " ' ’ ".strip().replace(" ", "")

_infixes = (
    LIST_ELLIPSES
    + LIST_ICONS
    + [
        r"(?<=[{a}][{el}])(?=[{a}])".format(a=ALPHA, el=ELISION),
        r"(?<=[{al}])\.(?=[{au}])".format(al=ALPHA_LOWER, au=ALPHA_UPPER),
        r"(?<=[{a}])[,!?](?=[{a}])".format(a=ALPHA),
        r"(?<=[{a}])[:<>=](?=[{a}])".format(a=ALPHA),
        r"(?<=[{a}]),(?=[{a}])".format(a=ALPHA),
        r"(?<=[{a}])--(?=[{a}])".format(a=ALPHA),
        r"(?<=[0-9])-(?=[0-9])",
    ]
)

TOKENIZER_INFIXES = _infixes
