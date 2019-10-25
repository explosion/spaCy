# coding: utf8
from __future__ import unicode_literals

from ...symbols import ORTH, LEMMA, NORM
from ..punctuation import TOKENIZER_PREFIXES

# TODO
# tokenize cliticised definite article "d'" as token of its own: d'Kanner > [d'] [Kanner]
# treat other apostrophes within words as part of the word: [op d'mannst], [fir d'éischt] (= exceptions)

# how to write the tokenisation exeption for the articles d' / D' ? This one is not working.
_prefixes = [
    prefix for prefix in TOKENIZER_PREFIXES if prefix not in ["d'", "D'", "d’", "D’"]
]


_exc = {
    "d'mannst": [
        {ORTH: "d'", LEMMA: "d'"},
        {ORTH: "mannst", LEMMA: "mann", NORM: "mann"},
    ],
    "d'éischt": [
        {ORTH: "d'", LEMMA: "d'"},
        {ORTH: "éischt", LEMMA: "éischt", NORM: "éischt"},
    ],
}

# translate / delete what is not necessary
# what does PRON_LEMMA mean?
for exc_data in [
    {ORTH: "wgl.", LEMMA: "wann ech gelift", NORM: "wann ech gelieft"},
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


TOKENIZER_PREFIXES = _prefixes
TOKENIZER_EXCEPTIONS = _exc
