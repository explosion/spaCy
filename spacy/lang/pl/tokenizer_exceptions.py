# encoding: utf8
from __future__ import unicode_literals

from ._tokenizer_exceptions_list import PL_BASE_EXCEPTIONS
from ...symbols import POS, ADV, NOUN, ORTH, LEMMA, ADJ


_exc = {}

for exc_data in [
    {ORTH: "m.in.", LEMMA: "między innymi", POS: ADV},
    {ORTH: "inż.", LEMMA: "inżynier", POS: NOUN},
    {ORTH: "mgr.", LEMMA: "magister", POS: NOUN},
    {ORTH: "tzn.", LEMMA: "to znaczy", POS: ADV},
    {ORTH: "tj.", LEMMA: "to jest", POS: ADV},
    {ORTH: "tzw.", LEMMA: "tak zwany", POS: ADJ},
]:
    _exc[exc_data[ORTH]] = [exc_data]

for orth in ["w.", "r."]:
    _exc[orth] = [{ORTH: orth}]

for orth in PL_BASE_EXCEPTIONS:
    _exc[orth] = [{ORTH: orth}]

TOKENIZER_EXCEPTIONS = _exc
