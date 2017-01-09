# encoding: utf8
from __future__ import unicode_literals

from ..symbols import *
from ..language_data import PRON_LEMMA


TOKENIZER_EXCEPTIONS = {
    "jan.": [
        {ORTH: "jan.", LEMMA: "januari"}
    ],
    "febr.": [
        {ORTH: "febr.", LEMMA: "februari"}
    ],
    "feb.": [
        {ORTH: "feb.", LEMMA: "februari"}
    ],
    "apr.": [
        {ORTH: "apr.", LEMMA: "april"}
    ],
    "jun.": [
        {ORTH: "jun.", LEMMA: "juni"}
    ],
    "jul.": [
        {ORTH: "jul.", LEMMA: "juli"}
    ],
    "aug.": [
        {ORTH: "aug.", LEMMA: "augusti"}
    ],
    "sept.": [
        {ORTH: "sept.", LEMMA: "september"}
    ],
    "sep.": [
        {ORTH: "sep.", LEMMA: "september"}
    ],
    "okt.": [
        {ORTH: "okt.", LEMMA: "oktober"}
    ],
    "nov.": [
        {ORTH: "nov.", LEMMA: "november"}
    ],
    "dec.": [
        {ORTH: "dec.", LEMMA: "december"}
    ],
    "mån.": [
        {ORTH: "mån.", LEMMA: "måndag"}
    ],
    "tis.": [
        {ORTH: "tis.", LEMMA: "tisdag"}
    ],
    "ons.": [
        {ORTH: "ons.", LEMMA: "onsdag"}
    ],
    "tors.": [
        {ORTH: "tors.", LEMMA: "torsdag"}
    ],
    "fre.": [
        {ORTH: "fre.", LEMMA: "fredag"}
    ],
    "lör.": [
        {ORTH: "lör.", LEMMA: "lördag"}
    ],
    "sön.": [
        {ORTH: "sön.", LEMMA: "söndag"}
    ],
    "sthlm": [
        {ORTH: "sthlm", LEMMA: "Stockholm"}
    ],
    "gbg": [
        {ORTH: "gbg", LEMMA: "Göteborg"}
    ]
}


ORTH_ONLY = [
    "ang.",
    "anm.",
    "bil.",
    "bl.a.",
    "dvs.",
    "e.Kr.",
    "el.",
    "e.d.",
    "eng.",
    "etc.",
    "exkl.",
    "f.d.",
    "fid.",
    "f.Kr.",
    "forts.",
    "fr.o.m.",
    "f.ö.",
    "förf.",
    "inkl.",
    "jur.",
    "kl.",
    "kr.",
    "lat.",
    "m.a.o.",
    "max.",
    "m.fl.",
    "min.",
    "m.m.",
    "obs.",
    "o.d.",
    "osv.",
    "p.g.a.",
    "ref.",
    "resp.",
    "s.",
    "s.a.s.",
    "s.k.",
    "st.",
    "s:t",
    "t.ex.",
    "t.o.m.",
    "ung.",
    "äv.",
    "övers."
]
