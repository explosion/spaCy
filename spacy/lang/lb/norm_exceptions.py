# coding: utf8
from __future__ import unicode_literals

# here one could include the most common spelling mistakes

_exc = {
    "datt": "dass",
    "wgl.": "weg.",
    "wgl.": "wegl.",
    "vläicht": "viläicht"}


NORM_EXCEPTIONS = {}

for string, norm in _exc.items():
    NORM_EXCEPTIONS[string] = norm
    NORM_EXCEPTIONS[string.title()] = norm