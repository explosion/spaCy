# coding: utf8
from __future__ import unicode_literals

from ...symbols import ORTH, LEMMA, NORM

# TODO
# treat other apostrophes within words as part of the word: [op d'mannst], [fir d'éischt] (= exceptions)

_exc = {}

# translate / delete what is not necessary
for exc_data in [
    {ORTH: "’t", LEMMA: "et", NORM: "et"},
    {ORTH: "’T", LEMMA: "et", NORM: "et"},
    {ORTH: "'t", LEMMA: "et", NORM: "et"},
    {ORTH: "'T", LEMMA: "et", NORM: "et"},
    {ORTH: "wgl.", LEMMA: "wannechgelift", NORM: "wannechgelift"},
    {ORTH: "M.", LEMMA: "Monsieur", NORM: "Monsieur"},
    {ORTH: "Mme.", LEMMA: "Madame", NORM: "Madame"},
    {ORTH: "Dr.", LEMMA: "Dokter", NORM: "Dokter"},
    {ORTH: "Tel.", LEMMA: "Telefon", NORM: "Telefon"},
    {ORTH: "asw.", LEMMA: "an sou weider", NORM: "an sou weider"},
    {ORTH: "etc.", LEMMA: "et cetera", NORM: "et cetera"},
    {ORTH: "bzw.", LEMMA: "bezéiungsweis", NORM: "bezéiungsweis"},
    {ORTH: "Jan.", LEMMA: "Januar", NORM: "Januar"},
]:
    _exc[exc_data[ORTH]] = [exc_data]


# to be extended
for orth in [
    "z.B.",
    "Dipl.",
    "Dr.",
    "etc.",
    "i.e.",
    "o.k.",
    "O.K.",
    "p.a.",
    "p.s.",
    "P.S.",
    "phil.",
    "q.e.d.",
    "R.I.P.",
    "rer.",
    "sen.",
    "ë.a.",
    "U.S.",
    "U.S.A.",
]:
    _exc[orth] = [{ORTH: orth}]

TOKENIZER_EXCEPTIONS = _exc
