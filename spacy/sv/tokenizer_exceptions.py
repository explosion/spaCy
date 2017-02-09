# encoding: utf8
from __future__ import unicode_literals

from ..symbols import *
from ..language_data import PRON_LEMMA


EXC = {}

# Verbs

for verb_data in [
    {ORTH: "driver"},
    {ORTH: "kör"},
    {ORTH: "hörr", LEMMA: "hör"},
    {ORTH: "fattar"},
    {ORTH: "hajar", LEMMA: "förstår"},
    {ORTH: "lever"},
    {ORTH: "serr", LEMMA: "ser"},
    {ORTH: "fixar"}
]:
    verb_data_tc = dict(verb_data)
    verb_data_tc[ORTH] = verb_data_tc[ORTH].title()

    for data in [verb_data, verb_data_tc]:
        EXC[data[ORTH] + "u"] = [
            dict(data),
            {ORTH: "u", LEMMA: PRON_LEMMA, NORM: "du"}
        ]


ABBREVIATIONS = {
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
    "Jan.": [
        {ORTH: "Jan.", LEMMA: "Januari"}
    ],
    "Febr.": [
        {ORTH: "Febr.", LEMMA: "Februari"}
    ],
    "Feb.": [
        {ORTH: "Feb.", LEMMA: "Februari"}
    ],
    "Apr.": [
        {ORTH: "Apr.", LEMMA: "April"}
    ],
    "Jun.": [
        {ORTH: "Jun.", LEMMA: "Juni"}
    ],
    "Jul.": [
        {ORTH: "Jul.", LEMMA: "Juli"}
    ],
    "Aug.": [
        {ORTH: "Aug.", LEMMA: "Augusti"}
    ],
    "Sept.": [
        {ORTH: "Sept.", LEMMA: "September"}
    ],
    "Sep.": [
        {ORTH: "Sep.", LEMMA: "September"}
    ],
    "Okt.": [
        {ORTH: "Okt.", LEMMA: "Oktober"}
    ],
    "Nov.": [
        {ORTH: "Nov.", LEMMA: "November"}
    ],
    "Dec.": [
        {ORTH: "Dec.", LEMMA: "December"}
    ],
    "Mån.": [
        {ORTH: "Mån.", LEMMA: "Måndag"}
    ],
    "Tis.": [
        {ORTH: "Tis.", LEMMA: "Tisdag"}
    ],
    "Ons.": [
        {ORTH: "Ons.", LEMMA: "Onsdag"}
    ],
    "Tors.": [
        {ORTH: "Tors.", LEMMA: "Torsdag"}
    ],
    "Fre.": [
        {ORTH: "Fre.", LEMMA: "Fredag"}
    ],
    "Lör.": [
        {ORTH: "Lör.", LEMMA: "Lördag"}
    ],
    "Sön.": [
        {ORTH: "Sön.", LEMMA: "Söndag"}
    ],
    "sthlm": [
        {ORTH: "sthlm", LEMMA: "Stockholm"}
    ],
    "gbg": [
        {ORTH: "gbg", LEMMA: "Göteborg"}
    ]
}


TOKENIZER_EXCEPTIONS = dict(EXC)
TOKENIZER_EXCEPTIONS.update(ABBREVIATIONS)


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
