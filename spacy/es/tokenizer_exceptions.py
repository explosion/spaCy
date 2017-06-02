# coding: utf8
from __future__ import unicode_literals

from ..symbols import *
from ..language_data import PRON_LEMMA, DET_LEMMA


TOKENIZER_EXCEPTIONS = {
    "pal": [
        {ORTH: "pa", LEMMA: "para"},
        {ORTH: "l", LEMMA: DET_LEMMA, NORM: "el"}
    ],

    "pala": [
        {ORTH: "pa", LEMMA: "para"},
        {ORTH: "la", LEMMA: DET_LEMMA, NORM: "la"}
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
    "a.C.",
    "a.J.C.",
    "apdo.",
    "Av.",
    "Avda.",
    "Cía.",
    "etc.",
    "Gob.",
    "Gral.",
    "Ing.",
    "J.C.",
    "Lic.",
    "m.n.",
    "no.",
    "núm.",
    "P.D.",
    "Prof.",
    "Profa.",
    "q.e.p.d."
    "S.A.",
    "S.L.",
    "s.s.s.",
    "Sr.",
    "Sra.",
    "Srta."
]
