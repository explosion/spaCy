# coding: utf8
from __future__ import unicode_literals

from ...symbols import LEMMA, NORM, ORTH, PRON_LEMMA

_exc = {}


# Verbs

for verb_data in [
    {ORTH: "driver"},
    {ORTH: "kör"},
    {ORTH: "hörr", LEMMA: "hör"},
    {ORTH: "fattar"},
    {ORTH: "hajar", LEMMA: "förstår"},
    {ORTH: "lever"},
    {ORTH: "serr", LEMMA: "ser"},
    {ORTH: "fixar"},
]:
    verb_data_tc = dict(verb_data)
    verb_data_tc[ORTH] = verb_data_tc[ORTH].title()
    for data in [verb_data, verb_data_tc]:
        _exc[data[ORTH] + "u"] = [
            dict(data),
            {ORTH: "u", LEMMA: PRON_LEMMA, NORM: "du"},
        ]

# Abbreviations for weekdays "sön." (for "söndag" / "söner")
# are left out because they are ambiguous. The same is the case
# for abbreviations "jul." and "Jul." ("juli" / "jul").
for exc_data in [
    {ORTH: "jan.", LEMMA: "januari"},
    {ORTH: "febr.", LEMMA: "februari"},
    {ORTH: "feb.", LEMMA: "februari"},
    {ORTH: "apr.", LEMMA: "april"},
    {ORTH: "jun.", LEMMA: "juni"},
    {ORTH: "aug.", LEMMA: "augusti"},
    {ORTH: "sept.", LEMMA: "september"},
    {ORTH: "sep.", LEMMA: "september"},
    {ORTH: "okt.", LEMMA: "oktober"},
    {ORTH: "nov.", LEMMA: "november"},
    {ORTH: "dec.", LEMMA: "december"},
    {ORTH: "mån.", LEMMA: "måndag"},
    {ORTH: "tis.", LEMMA: "tisdag"},
    {ORTH: "ons.", LEMMA: "onsdag"},
    {ORTH: "tors.", LEMMA: "torsdag"},
    {ORTH: "fre.", LEMMA: "fredag"},
    {ORTH: "lör.", LEMMA: "lördag"},
    {ORTH: "Jan.", LEMMA: "Januari"},
    {ORTH: "Febr.", LEMMA: "Februari"},
    {ORTH: "Feb.", LEMMA: "Februari"},
    {ORTH: "Apr.", LEMMA: "April"},
    {ORTH: "Jun.", LEMMA: "Juni"},
    {ORTH: "Aug.", LEMMA: "Augusti"},
    {ORTH: "Sept.", LEMMA: "September"},
    {ORTH: "Sep.", LEMMA: "September"},
    {ORTH: "Okt.", LEMMA: "Oktober"},
    {ORTH: "Nov.", LEMMA: "November"},
    {ORTH: "Dec.", LEMMA: "December"},
    {ORTH: "Mån.", LEMMA: "Måndag"},
    {ORTH: "Tis.", LEMMA: "Tisdag"},
    {ORTH: "Ons.", LEMMA: "Onsdag"},
    {ORTH: "Tors.", LEMMA: "Torsdag"},
    {ORTH: "Fre.", LEMMA: "Fredag"},
    {ORTH: "Lör.", LEMMA: "Lördag"},
    {ORTH: "sthlm", LEMMA: "Stockholm"},
    {ORTH: "gbg", LEMMA: "Göteborg"},
]:
    _exc[exc_data[ORTH]] = [exc_data]


# Specific case abbreviations only
for orth in ["AB", "Dr.", "H.M.", "H.K.H.", "m/s", "M/S", "Ph.d.", "S:t", "s:t"]:
    _exc[orth] = [{ORTH: orth}]


ABBREVIATIONS = [
    "ang",
    "anm",
    "bl.a",
    "d.v.s",
    "doc",
    "dvs",
    "e.d",
    "e.kr",
    "el.",
    "eng",
    "etc",
    "exkl",
    "ev",
    "f.",
    "f.d",
    "f.kr",
    "f.n",
    "f.ö",
    "fid",
    "fig",
    "forts",
    "fr.o.m",
    "förf",
    "inkl",
    "iofs",
    "jur.",
    "kap",
    "kl",
    "kor.",
    "kr",
    "kungl",
    "lat",
    "m.a.o",
    "m.fl",
    "m.m",
    "max",
    "milj",
    "min.",
    "mos",
    "mt",
    "mvh",
    "o.d",
    "o.s.v",
    "obs",
    "osv",
    "p.g.a",
    "proc",
    "prof",
    "ref",
    "resp",
    "s.a.s",
    "s.k",
    "s.t",
    "sid",
    "t.ex",
    "t.h",
    "t.o.m",
    "t.v",
    "tel",
    "ung.",
    "vol",
    "v.",
    "äv",
    "övers",
]

# Add abbreviation for trailing punctuation too. If the abbreviation already has a trailing punctuation - skip it.
for abbr in ABBREVIATIONS:
    if not abbr.endswith("."):
        ABBREVIATIONS.append(abbr + ".")

for orth in ABBREVIATIONS:
    _exc[orth] = [{ORTH: orth}]
    capitalized = orth.capitalize()
    _exc[capitalized] = [{ORTH: capitalized}]

# Sentences ending in "i." (as in "... peka i."), "m." (as in "...än 2000 m."),
# should be tokenized as two separate tokens.
for orth in ["i", "m"]:
    _exc[orth + "."] = [{ORTH: orth, LEMMA: orth, NORM: orth}, {ORTH: "."}]

TOKENIZER_EXCEPTIONS = _exc
