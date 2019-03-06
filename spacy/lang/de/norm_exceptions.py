# coding: utf8
from __future__ import unicode_literals

# Here we only want to include the absolute most common words. Otherwise,
# this list would get impossibly long for German – especially considering the
# old vs. new spelling rules, and all possible cases.


_exc = {"daß": "dass"}


NORM_EXCEPTIONS = {}

for string, norm in _exc.items():
    NORM_EXCEPTIONS[string] = norm
    NORM_EXCEPTIONS[string.title()] = norm
