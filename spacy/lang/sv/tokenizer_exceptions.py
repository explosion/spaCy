# coding: utf8
from __future__ import unicode_literals

from ...symbols import LEMMA, NORM, ORTH, PRON_LEMMA, PUNCT, TAG

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
    {ORTH: "fixar"}]:
    verb_data_tc = dict(verb_data)
    verb_data_tc[ORTH] = verb_data_tc[ORTH].title()
    for data in [verb_data, verb_data_tc]:
        _exc[data[ORTH] + "u"] = [
            dict(data),
            {ORTH: "u", LEMMA: PRON_LEMMA, NORM: "du"}]


for exc_data in [
    {ORTH: "jan.", LEMMA: "januari"},
    {ORTH: "febr.", LEMMA: "februari"},
    {ORTH: "feb.", LEMMA: "februari"},
    {ORTH: "apr.", LEMMA: "april"},
    {ORTH: "jun.", LEMMA: "juni"},
    {ORTH: "jul.", LEMMA: "juli"},
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
    {ORTH: "sön.", LEMMA: "söndag"},
    {ORTH: "Jan.", LEMMA: "Januari"},
    {ORTH: "Febr.", LEMMA: "Februari"},
    {ORTH: "Feb.", LEMMA: "Februari"},
    {ORTH: "Apr.", LEMMA: "April"},
    {ORTH: "Jun.", LEMMA: "Juni"},
    {ORTH: "Jul.", LEMMA: "Juli"},
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
    {ORTH: "Sön.", LEMMA: "Söndag"},
    {ORTH: "sthlm", LEMMA: "Stockholm"},
    {ORTH: "gbg", LEMMA: "Göteborg"}]:
    _exc[exc_data[ORTH]] = [exc_data]


ABBREVIATIONS = [
    "ang", "anm", "bil", "bl.a", "d.v.s", "doc", "dvs", "e.d", "e.kr", "el",
    "eng", "etc", "exkl", "f", "f.d", "f.kr", "f.n", "f.ö", "fid", "fig",
    "forts", "fr.o.m", "förf", "inkl", "jur", "kap", "kl", "kor", "kr",
    "kungl", "lat", "m.a.o", "m.fl", "m.m", "max", "milj", "min", "mos",
    "mt", "o.d", "o.s.v", "obs", "osv", "p.g.a", "proc", "prof", "ref",
    "resp", "s.a.s", "s.k", "s.t", "sid", "s:t", "t.ex", "t.h", "t.o.m", "t.v",
    "tel", "ung", "vol", "äv", "övers"
]
ABBREVIATIONS = [abbr + "." for abbr in ABBREVIATIONS] + ABBREVIATIONS

for orth in ABBREVIATIONS:
    _exc[orth] = [{ORTH: orth}]

# Sentences ending in "i." (as in "... peka i."), "m." (as in "...än 2000 m."),
# should be tokenized as two separate tokens.
for orth in ["i", "m"]:
    _exc[orth + "."] = [
        {ORTH: orth, LEMMA: orth, NORM: orth},
        {ORTH: ".", TAG: PUNCT}]

TOKENIZER_EXCEPTIONS = _exc
