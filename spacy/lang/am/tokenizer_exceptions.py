# coding: utf8
from __future__ import unicode_literals

from ...symbols import ORTH, LEMMA, NORM, PRON_LEMMA


_exc = {}


for exc_data in [
    {ORTH: "ት/ቤት", LEMMA: "ትምህርት ቤት"},
    {ORTH: "ጽ/ቤት", LEMMA: "ጽህፈት ቤት", NORM: "ጽህፈት ቤት"},
    {ORTH: "ፅ/ቤት", LEMMA: "ጽህፈት ቤት", NORM: "ጽህፈት ቤት"},
    {ORTH: "መ/ቤት", LEMMA: "መስሪያ ቤት", NORM: "መስሪያ ቤት"},
    {ORTH: "ም/ቤት", LEMMA: "ምክር ቤት", NORM: "ምክር ቤት"},
    {ORTH: "ፍ/ቤት", LEMMA: "ፍርድ ቤት", NORM: "ፍርድ ቤት"},    
    {ORTH: "ወ/ሮ", LEMMA: PRON_LEMMA, NORM: "ወይዘሮ"},

]:
    _exc[exc_data[ORTH]] = [exc_data]


for orth in [
    "ዓ.ም.",
    "ኪ.ሜ.",
]:
    _exc[orth] = [{ORTH: orth}]


TOKENIZER_EXCEPTIONS = _exc
