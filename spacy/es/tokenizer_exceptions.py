# encoding: utf8
from __future__ import unicode_literals

from ..symbols import *
from ..language_data import PRON_LEMMA, DET_LEMMA


TOKENIZER_EXCEPTIONS = {
    "al": [
        {ORTH: "a", LEMMA: "a", TAG: ADP},
        {ORTH: "el", LEMMA: "el", TAG: DET}
    ],

    "consigo": [
        {ORTH: "con", LEMMA: "con"},
        {ORTH: "sigo", LEMMA: PRON_LEMMA, NORM: "sí"}
    ],

    "conmigo": [
        {ORTH: "con", LEMMA: "con"},
        {ORTH: "migo", LEMMA: PRON_LEMMA, NORM: "mí"}
    ],

    "contigo": [
        {ORTH: "con", LEMMA: "con"},
        {ORTH: "tigo", LEMMA: PRON_LEMMA, NORM: "ti"}
    ],

    "del": [
        {ORTH: "de", LEMMA: "de", TAG: ADP},
        {ORTH: "l", LEMMA: "el", TAG: DET}
    ],

    "pel": [
        {ORTH: "pe", LEMMA: "per", TAG: ADP},
        {ORTH: "l", LEMMA: "el", TAG: DET}
    ],

    "pal": [
        {ORTH: "pa", LEMMA: "para"},
        {ORTH: "l", LEMMA: DET_LEMMA, NORM: "el"}
    ],

    "pala": [
        {ORTH: "pa", LEMMA: "para"},
        {ORTH: "la", LEMMA: DET_LEMMA}
    ],

    "aprox.": [
        {ORTH: "aprox.", LEMMA: "aproximadamente"}
    ],

    "dna.": [
        {ORTH: "dna.", LEMMA: "docena"}
    ],

    "esq.": [
        {ORTH: "esq.", LEMMA: "esquina"}
    ],

    "pág.": [
        {ORTH: "pág.", LEMMA: "página"}
    ],

    "p.ej.": [
        {ORTH: "p.ej.", LEMMA: "por ejemplo"}
    ],

    "Ud.": [
        {ORTH: "Ud.", LEMMA: PRON_LEMMA, NORM: "usted"}
    ],

    "Vd.": [
        {ORTH: "Vd.", LEMMA: PRON_LEMMA, NORM: "usted"}
    ],

    "Uds.": [
        {ORTH: "Uds.", LEMMA: PRON_LEMMA, NORM: "ustedes"}
    ],

    "Vds.": [
        {ORTH: "Vds.", LEMMA: PRON_LEMMA, NORM: "ustedes"}
    ]
}


ORTH_ONLY = [
    "a.",
    "a.C.",
    "a.J.C.",
    "apdo.",
    "Av.",
    "Avda.",
    "b.",
    "c.",
    "Cía.",
    "d.",
    "e.",
    "etc.",
    "f.",
    "g.",
    "Gob.",
    "Gral.",
    "h.",
    "i.",
    "Ing.",
    "j.",
    "J.C.",
    "k.",
    "l.",
    "Lic.",
    "m.",
    "m.n.",
    "n.",
    "no.",
    "núm.",
    "o.",
    "p.",
    "P.D.",
    "Prof.",
    "Profa.",
    "q.",
    "q.e.p.d."
    "r.",
    "s.",
    "S.A.",
    "S.L.",
    "s.s.s.",
    "Sr.",
    "Sra.",
    "Srta.",
    "t.",
    "u.",
    "v.",
    "w.",
    "x.",
    "y.",
    "z."
]
