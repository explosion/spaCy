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
        {ORTH: "d'", LEMMA: "mo", NORM: "do"}
    ],

    "m'": [
        {ORTH: "m'", LEMMA: "mo", NORM: "mo"}
    ],

    "a.C.n.": [
        {ORTH: "a.", LEMMA: "ante"},
        {ORTH: "C.", LEMMA: "Christum"},
        {ORTH: "n.", LEMMA: "natum"},
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
        {ORTH: "m.", LEMMA: "mar"},
        {ORTH: "sh.", LEMMA: "sampla"}
    ],

    "Már.": [
        {ORTH: "Már.", LEMMA: "Márta"}
    ],

    "Meith.": [
        {ORTH: "Meith.", LEMMA: "Meitheamh"}
    ],

    "M.F.": [
        {ORTH: "M.", LEMMA: "Meán"},
        {ORTH: "F.", LEMMA: "Fómhar"}
    ],

    "M.Fómh.": [
        {ORTH: "M.", LEMMA: "Meán"},
        {ORTH: "Fómh.", LEMMA: "Fómhar"}
    ],

    "Noll.": [
        {ORTH: "Noll.", LEMMA: "Nollaig"}
    ],

    "R.C.": [
        {ORTH: "Rr.", LEMMA: "roimh"},
        {ORTH: "C.", LEMMA: "Críost"}
    ],

    "r.Ch.": [
        {ORTH: "r.", LEMMA: "roimh"},
        {ORTH: "Ch.", LEMMA: "Críost"}
    ],

    "r.Chr.": [
        {ORTH: "r.", LEMMA: "roimh"},
        {ORTH: "Chr.", LEMMA: "Críost"}
    ],

    "R.Ch.": [
        {ORTH: "R.", LEMMA: "roimh"},
        {ORTH: "Ch.", LEMMA: "Críost"}
    ],

    "R.Chr.": [
        {ORTH: "R.", LEMMA: "roimh"},
        {ORTH: "Chr.", LEMMA: "Críost"}
    ],

    "Samh.": [
        {ORTH: "Samh.", LEMMA: "Samhain"}
    ],

    "⁊rl.": [
        {ORTH: "⁊", LEMMA: "agus"},
        {ORTH: "rl.", LEMMA: "araile"}
    ],

    "srl.": [
        {ORTH: "s", LEMMA: "agus"},
        {ORTH: "rl.", LEMMA: "araile"}
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

}

ORTH_ONLY = [
    "d'",
]
