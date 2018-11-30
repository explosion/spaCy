# encoding: utf8
from __future__ import unicode_literals

from ...symbols import POS, DET, ADP, CCONJ, ADV, NOUN, X, AUX
from ...symbols import ORTH, LEMMA, NORM


_exc = {
    "'acha'n": [
        {ORTH: "'ach", LEMMA: "gach", NORM: "gach", POS: DET},
        {ORTH: "a'n", LEMMA: "aon", NORM: "aon", POS: DET},
    ],
    "dem'": [
        {ORTH: "de", LEMMA: "de", NORM: "de", POS: ADP},
        {ORTH: "m'", LEMMA: "mo", NORM: "mo", POS: DET},
    ],
    "ded'": [
        {ORTH: "de", LEMMA: "de", NORM: "de", POS: ADP},
        {ORTH: "d'", LEMMA: "do", NORM: "do", POS: DET},
    ],
    "lem'": [
        {ORTH: "le", LEMMA: "le", NORM: "le", POS: ADP},
        {ORTH: "m'", LEMMA: "mo", NORM: "mo", POS: DET},
    ],
    "led'": [
        {ORTH: "le", LEMMA: "le", NORM: "le", POS: ADP},
        {ORTH: "d'", LEMMA: "mo", NORM: "do", POS: DET},
    ],
}

for exc_data in [
    {ORTH: "'gus", LEMMA: "agus", NORM: "agus", POS: CCONJ},
    {ORTH: "'ach", LEMMA: "gach", NORM: "gach", POS: DET},
    {ORTH: "ao'", LEMMA: "aon", NORM: "aon"},
    {ORTH: "'niar", LEMMA: "aniar", NORM: "aniar", POS: ADV},
    {ORTH: "'níos", LEMMA: "aníos", NORM: "aníos", POS: ADV},
    {ORTH: "'ndiu", LEMMA: "inniu", NORM: "inniu", POS: ADV},
    {ORTH: "'nocht", LEMMA: "anocht", NORM: "anocht", POS: ADV},
    {ORTH: "m'", LEMMA: "mo", POS: DET},
    {ORTH: "Aib.", LEMMA: "Aibreán", POS: NOUN},
    {ORTH: "Ath.", LEMMA: "athair", POS: NOUN},
    {ORTH: "Beal.", LEMMA: "Bealtaine", POS: NOUN},
    {ORTH: "a.C.n.", LEMMA: "ante Christum natum", POS: X},
    {ORTH: "m.sh.", LEMMA: "mar shampla", POS: ADV},
    {ORTH: "M.F.", LEMMA: "Meán Fómhair", POS: NOUN},
    {ORTH: "M.Fómh.", LEMMA: "Meán Fómhair", POS: NOUN},
    {ORTH: "D.F.", LEMMA: "Deireadh Fómhair", POS: NOUN},
    {ORTH: "D.Fómh.", LEMMA: "Deireadh Fómhair", POS: NOUN},
    {ORTH: "r.C.", LEMMA: "roimh Chríost", POS: ADV},
    {ORTH: "R.C.", LEMMA: "roimh Chríost", POS: ADV},
    {ORTH: "r.Ch.", LEMMA: "roimh Chríost", POS: ADV},
    {ORTH: "r.Chr.", LEMMA: "roimh Chríost", POS: ADV},
    {ORTH: "R.Ch.", LEMMA: "roimh Chríost", POS: ADV},
    {ORTH: "R.Chr.", LEMMA: "roimh Chríost", POS: ADV},
    {ORTH: "⁊rl.", LEMMA: "agus araile", POS: ADV},
    {ORTH: "srl.", LEMMA: "agus araile", POS: ADV},
    {ORTH: "Co.", LEMMA: "contae", POS: NOUN},
    {ORTH: "Ean.", LEMMA: "Eanáir", POS: NOUN},
    {ORTH: "Feab.", LEMMA: "Feabhra", POS: NOUN},
    {ORTH: "gCo.", LEMMA: "contae", POS: NOUN},
    {ORTH: ".i.", LEMMA: "eadhon", POS: ADV},
    {ORTH: "B'", LEMMA: "ba", POS: AUX},
    {ORTH: "b'", LEMMA: "ba", POS: AUX},
    {ORTH: "lch.", LEMMA: "leathanach", POS: NOUN},
    {ORTH: "Lch.", LEMMA: "leathanach", POS: NOUN},
    {ORTH: "lgh.", LEMMA: "leathanach", POS: NOUN},
    {ORTH: "Lgh.", LEMMA: "leathanach", POS: NOUN},
    {ORTH: "Lún.", LEMMA: "Lúnasa", POS: NOUN},
    {ORTH: "Már.", LEMMA: "Márta", POS: NOUN},
    {ORTH: "Meith.", LEMMA: "Meitheamh", POS: NOUN},
    {ORTH: "Noll.", LEMMA: "Nollaig", POS: NOUN},
    {ORTH: "Samh.", LEMMA: "Samhain", POS: NOUN},
    {ORTH: "tAth.", LEMMA: "athair", POS: NOUN},
    {ORTH: "tUas.", LEMMA: "Uasal", POS: NOUN},
    {ORTH: "teo.", LEMMA: "teoranta", POS: NOUN},
    {ORTH: "Teo.", LEMMA: "teoranta", POS: NOUN},
    {ORTH: "Uas.", LEMMA: "Uasal", POS: NOUN},
    {ORTH: "uimh.", LEMMA: "uimhir", POS: NOUN},
    {ORTH: "Uimh.", LEMMA: "uimhir", POS: NOUN},
]:
    _exc[exc_data[ORTH]] = [exc_data]

for orth in ["d'", "D'"]:
    _exc[orth] = [{ORTH: orth}]


TOKENIZER_EXCEPTIONS = _exc
