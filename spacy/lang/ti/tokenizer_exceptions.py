# coding: utf8
from __future__ import unicode_literals

from ...symbols import ORTH, LEMMA, NORM, PRON_LEMMA


_exc = {}


for exc_data in [
    {ORTH: "ት/ቤት", LEMMA: "ትምህርት ቤት"},    
    {ORTH: "ወ/ሮ", LEMMA: PRON_LEMMA, NORM: "ወይዘሮ"},
    {ORTH: "ወ/ሪ", LEMMA: PRON_LEMMA, NORM: "ወይዘሪት"},

]:
    _exc[exc_data[ORTH]] = [exc_data]


for orth in [
    "ዓ.ም.",
    "ኪ.ሜ.",
]:
    _exc[orth] = [{ORTH: orth}]


TOKENIZER_EXCEPTIONS = _exc
