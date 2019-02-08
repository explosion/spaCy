# coding: utf8
from __future__ import unicode_literals

from ...symbols import ORTH, LEMMA, POS, NORM, NOUN


_exc = {}

for exc_data in [
    {ORTH: "вул.", LEMMA: "вулиця", NORM: "вулиця", POS: NOUN},
    {ORTH: "ім.", LEMMA: "ім'я", NORM: "імені", POS: NOUN},
    {ORTH: "просп.", LEMMA: "проспект", NORM: "проспект", POS: NOUN},
    {ORTH: "бул.", LEMMA: "бульвар", NORM: "бульвар", POS: NOUN},
    {ORTH: "пров.", LEMMA: "провулок", NORM: "провулок", POS: NOUN},
    {ORTH: "пл.", LEMMA: "площа", NORM: "площа", POS: NOUN},
    {ORTH: "г.", LEMMA: "гора", NORM: "гора", POS: NOUN},
    {ORTH: "п.", LEMMA: "пан", NORM: "пан", POS: NOUN},
    {ORTH: "м.", LEMMA: "місто", NORM: "місто", POS: NOUN},
    {ORTH: "проф.", LEMMA: "професор", NORM: "професор", POS: NOUN},
    {ORTH: "акад.", LEMMA: "академік", NORM: "академік", POS: NOUN},
    {ORTH: "доц.", LEMMA: "доцент", NORM: "доцент", POS: NOUN},
    {ORTH: "оз.", LEMMA: "озеро", NORM: "озеро", POS: NOUN},
]:
    _exc[exc_data[ORTH]] = [exc_data]


TOKENIZER_EXCEPTIONS = _exc
