# encoding: utf8
# Irish
from __future__ import unicode_literals

from ..symbols import *

TOKENIZER_EXCEPTIONS = {
    "'gus": [
        {ORTH: "'gus", LEMMA: "agus", NORM: "agus"}
    ],

    "'ach": [
        {ORTH: "'ach", LEMMA: "gach", NORM: "gach"}
    ],

    "'acha'n": [
        {ORTH: "'ach", LEMMA: "gach", NORM: "gach"},
        {ORTH: "a'n", LEMMA: "aon", NORM: "aon"}
    ],

    "ao'": [
        {ORTH: "ao'", LEMMA: "aon", NORM: "aon"}
    ],

    "'niar": [
        {ORTH: "'niar", LEMMA: "aniar", NORM: "aniar"}
    ],

    "'níos": [
        {ORTH: "'níos", LEMMA: "aníos", NORM: "aníos"}
    ],

    "'ndiu": [
        {ORTH: "'ndiu", LEMMA: "inniu", NORM: "inniu"}
    ],

    "'nocht": [
        {ORTH: "'nocht", LEMMA: "anocht", NORM: "anocht"}
    ],

    "dem'": [
        {ORTH: "de", LEMMA: "de", NORM: "de"},
        {ORTH: "m'", LEMMA: "mo", NORM: "mo"}
    ],

    "ded'": [
        {ORTH: "de", LEMMA: "de", NORM: "de"},
        {ORTH: "d'", LEMMA: "do", NORM: "do"}
    ],

    "lem'": [
        {ORTH: "le", LEMMA: "le", NORM: "le"},
        {ORTH: "m'", LEMMA: "mo", NORM: "mo"}
    ],

    "led'": [
        {ORTH: "le", LEMMA: "le", NORM: "le"},
        {ORTH: "d'", LEMMA: "do", NORM: "do"}
    ],

    "m'": [
        {ORTH: "m'", LEMMA: "mo"}
    ],

    "a.C.n.": [
        {ORTH: "a.C.n.", LEMMA: "ante Christum natum"}
    ],

    "Aib.": [
        {ORTH: "Aib.", LEMMA: "Aibreán"}
    ],

    "Ath.": [
        {ORTH: "Ath.", LEMMA: "athair"}
    ],

    "Beal.": [
        {ORTH: "Beal.", LEMMA: "Bealtaine"}
    ],

    "Co.": [
        {ORTH: "Co.", LEMMA: "contae"}
    ],

    "Ean.": [
        {ORTH: "Ean.", LEMMA: "Eanáir"}
    ],

    "Feab.": [
        {ORTH: "Feab.", LEMMA: "Feabhra"}
    ],

    "gCo.": [
        {ORTH: "gCo.", LEMMA: "contae"}
    ],

    ".i.": [
        {ORTH: ".i.", LEMMA: "eadhon"}
    ],

    "lch.": [
        {ORTH: "lch.", LEMMA: "leathanach"}
    ],

    "Lch.": [
        {ORTH: "Lch.", LEMMA: "leathanach"}
    ],

    "lgh.": [
        {ORTH: "lgh.", LEMMA: "leathanach"}
    ],

    "Lgh.": [
        {ORTH: "Lgh.", LEMMA: "leathanach"}
    ],

    "Lún.": [
        {ORTH: "Lún.", LEMMA: "Lúnasa"}
    ],

    "m.sh.": [
        {ORTH: "m.sh.", LEMMA: "mar shampla"}
    ],

    "Már.": [
        {ORTH: "Már.", LEMMA: "Márta"}
    ],

    "Meith.": [
        {ORTH: "Meith.", LEMMA: "Meitheamh"}
    ],

    "M.F.": [
        {ORTH: "M.F.", LEMMA: "Meán Fómhair"}
    ],

    "M.Fómh.": [
        {ORTH: "M.Fómh.", LEMMA: "Meán Fómhair"}
    ],

    "D.F.": [
        {ORTH: "D.F.", LEMMA: "Deireadh Fómhair"}
    ],

    "D.Fómh.": [
        {ORTH: "D.Fómh.", LEMMA: "Deireadh Fómhair"}
    ],

    "Noll.": [
        {ORTH: "Noll.", LEMMA: "Nollaig"}
    ],

    "R.C.": [
        {ORTH: "R.C.", LEMMA: "roimh Chríost"}
    ],

    "r.Ch.": [
        {ORTH: "r.Ch.", LEMMA: "roimh Chríost"}
    ],

    "r.Chr.": [
        {ORTH: "r.Chr.", LEMMA: "roimh Chríost"}
    ],

    "R.Ch.": [
        {ORTH: "R.Ch.", LEMMA: "roimh Chríost"}
    ],

    "R.Chr.": [
        {ORTH: "R.Chr.", LEMMA: "roimh Chríost"}
    ],

    "Samh.": [
        {ORTH: "Samh.", LEMMA: "Samhain"}
    ],

    "⁊rl.": [
        {ORTH: "⁊rl.", LEMMA: "agus araile"}
    ],

    "srl.": [
        {ORTH: "srl.", LEMMA: "agus araile"}
    ],

    "tAth.": [
        {ORTH: "tAth.", LEMMA: "athair"}
    ],

    "tUas.": [
        {ORTH: "tUas.", LEMMA: "Uasal"}
    ],

    "teo.": [
        {ORTH: "teo.", LEMMA: "teoranta"}
    ],

    "Teo.": [
        {ORTH: "Teo.", LEMMA: "teoranta"}
    ],

    "Uas.": [
        {ORTH: "Uas.", LEMMA: "Uasal"}
    ],

    "uimh.": [
        {ORTH: "uimh.", LEMMA: "uimhir"}
    ],

    "Uimh.": [
        {ORTH: "Uimh.", LEMMA: "uimhir"}
    ],

    "B'": [
        {ORTH: "B'", LEMMA: "ba"}
    ],

    "b'": [
        {ORTH: "b'", LEMMA: "ba"}
    ],
}

ORTH_ONLY = [
    "d'", "D'"
]
