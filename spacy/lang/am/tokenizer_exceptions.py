# coding: utf8
from __future__ import unicode_literals

from ...symbols import ORTH, LEMMA, NORM, PRON_LEMMA


_exc = {}


for exc_data in [
    {ORTH: "ት/ቤት", LEMMA: "ትምህርት ቤት"},

]:
    _exc[exc_data[ORTH]] = [exc_data]


# Times

#_exc["12m."] = [{ORTH: "12"}, {ORTH: "m.", LEMMA: "p.m."}]


for h in range(1, 12 + 1):
    for period in ["a.m.", "am"]:
        _exc["%d%s" % (h, period)] = [{ORTH: "%d" % h}, {ORTH: period, LEMMA: "a.m."}]
    for period in ["p.m.", "pm"]:
        _exc["%d%s" % (h, period)] = [{ORTH: "%d" % h}, {ORTH: period, LEMMA: "p.m."}]


for orth in [
    "ዓ.ም."
]:
    _exc[orth] = [{ORTH: orth}]


TOKENIZER_EXCEPTIONS = _exc
