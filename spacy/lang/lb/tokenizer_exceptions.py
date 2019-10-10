# coding: utf8
from __future__ import unicode_literals

from ...symbols import ORTH, LEMMA, TAG, NORM, PRON_LEMMA
from ..punctuation import TOKENIZER_PREFIXES

# how to write the tokenisation exeption for the articles d' / D' ? This one is not working.
_prefixes = [prefix for prefix in TOKENIZER_PREFIXES if prefix not in ["d'", "D'", "d’", "D’", r"\' "]]


_exc = {
    "d'mannst": [
        {ORTH: "d'", LEMMA: "d'"},
        {ORTH: "mannst", LEMMA: "mann", NORM: "mann"}],
    "d'éischt": [
        {ORTH: "d'", LEMMA: "d'"},
        {ORTH: "éischt", LEMMA: "éischt", NORM: "éischt"}]
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
    {ORTH: "bzw.", LEMMA: "bezéiungsweis", NORM: "bezéiungsweis"}]:
    _exc[exc_data[ORTH]] = [exc_data]


# necessary for Luxembourgish?
for orth in [
    "A.C.", "a.D.", "A.D.", "A.G.", "a.M.", "a.Z.", "Abs.", "adv.", "al.",
    "B.A.", "B.Sc.", "betr.", "biol.", "Biol.", "ca.", "Chr.", "Cie.", "co.",
    "Co.", "D.C.", "Dipl.-Ing.", "Dipl.", "Dr.", "e.g.", "e.V.", "ehem.",
    "entspr.", "erm.", "etc.", "ev.", "G.m.b.H.", "geb.", "Gebr.", "gem.",
    "h.c.", "Hg.", "hrsg.", "Hrsg.", "i.A.", "i.e.", "i.G.", "i.Tr.", "i.V.",
    "Ing.", "jr.", "Jr.", "jun.", "jur.", "K.O.", "L.A.", "lat.", "M.A.",
    "m.E.", "m.M.", "M.Sc.", "Mr.", "N.Y.", "N.Y.C.", "nat.", "o.a.",
    "o.ä.", "o.g.", "o.k.", "O.K.", "p.a.", "p.s.", "P.S.", "pers.", "phil.",
    "q.e.d.", "R.I.P.", "rer.", "sen.", "St.", "std.", "u.a.", "U.S.", "U.S.A.",
    "U.S.S.", "Vol.", "vs.", "wiss."]:
    _exc[orth] = [{ORTH: orth}]


TOKENIZER_PREFIXES = _prefixes
TOKENIZER_EXCEPTIONS = _exc
