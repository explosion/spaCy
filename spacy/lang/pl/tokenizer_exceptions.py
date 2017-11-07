# encoding: utf8
from __future__ import unicode_literals

from ...symbols import ORTH, LEMMA, POS, ADV, ADJ, NOUN


_exc = {}

for exc_data in [
    {ORTH: "m.in.", LEMMA: "między innymi", POS: ADV},
    {ORTH: "inż.", LEMMA: "inżynier", POS: NOUN},
    {ORTH: "mgr.", LEMMA: "magister", POS: NOUN},
    {ORTH: "tzn.", LEMMA: "to znaczy", POS: ADV},
    {ORTH: "tj.", LEMMA: "to jest", POS: ADV},
    {ORTH: "tzw.", LEMMA: "tak zwany", POS: ADJ}]:
    _exc[exc_data[ORTH]] = [exc_data]

for orth in [
    "w.", "r."]:
    _exc[orth] = [{ORTH: orth}]


TOKENIZER_EXCEPTIONS = _exc
