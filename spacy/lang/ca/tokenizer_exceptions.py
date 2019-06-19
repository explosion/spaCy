# coding: utf8
from __future__ import unicode_literals

from ...symbols import ORTH, LEMMA


_exc = {}

for exc_data in [
    {ORTH: "aprox.", LEMMA: "aproximadament"},
    {ORTH: "pàg.", LEMMA: "pàgina"},
    {ORTH: "p.ex.", LEMMA: "per exemple"},
    {ORTH: "gen.", LEMMA: "gener"},
    {ORTH: "feb.", LEMMA: "febrer"},
    {ORTH: "abr.", LEMMA: "abril"},
    {ORTH: "jul.", LEMMA: "juliol"},
    {ORTH: "set.", LEMMA: "setembre"},
    {ORTH: "oct.", LEMMA: "octubre"},
    {ORTH: "nov.", LEMMA: "novembre"},
    {ORTH: "dec.", LEMMA: "desembre"},
    {ORTH: "Dr.", LEMMA: "doctor"},
    {ORTH: "Sr.", LEMMA: "senyor"},
    {ORTH: "Sra.", LEMMA: "senyora"},
    {ORTH: "Srta.", LEMMA: "senyoreta"},
    {ORTH: "núm", LEMMA: "número"},
    {ORTH: "St.", LEMMA: "sant"},
    {ORTH: "Sta.", LEMMA: "santa"},
]:
    _exc[exc_data[ORTH]] = [exc_data]

# Times
_exc["12m."] = [{ORTH: "12"}, {ORTH: "m.", LEMMA: "p.m."}]

for h in range(1, 12 + 1):
    for period in ["a.m.", "am"]:
        _exc["%d%s" % (h, period)] = [{ORTH: "%d" % h}, {ORTH: period, LEMMA: "a.m."}]
    for period in ["p.m.", "pm"]:
        _exc["%d%s" % (h, period)] = [{ORTH: "%d" % h}, {ORTH: period, LEMMA: "p.m."}]


TOKENIZER_EXCEPTIONS = _exc
