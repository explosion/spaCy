# coding: utf8
from __future__ import unicode_literals

# TODO
# norm execptions: find a possibility to deal with the zillions of spelling
# variants (vläicht = vlaicht, vleicht, viläicht, viläischt, etc. etc.)
# here one could include the most common spelling mistakes

_exc = {"dass": "datt", "viläicht": "vläicht"}


NORM_EXCEPTIONS = {}

for string, norm in _exc.items():
    NORM_EXCEPTIONS[string] = norm
    NORM_EXCEPTIONS[string.title()] = norm
