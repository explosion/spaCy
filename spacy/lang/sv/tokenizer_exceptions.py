# coding: utf8
from __future__ import unicode_literals

from ...symbols import ORTH, LEMMA, TAG, NORM, PRON_LEMMA


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


for orth in [
    "ang.", "anm.", "bil.", "bl.a.", "dvs.", "e.Kr.", "el.", "e.d.", "eng.",
    "etc.", "exkl.", "f.d.", "fid.", "f.Kr.", "forts.", "fr.o.m.", "f.ö.",
    "förf.", "inkl.", "jur.", "kl.", "kr.", "lat.", "m.a.o.", "max.", "m.fl.",
    "min.", "m.m.", "obs.", "o.d.", "osv.", "p.g.a.", "ref.", "resp.", "s.a.s.",
    "s.k.", "st.", "s:t", "t.ex.", "t.o.m.", "ung.", "äv.", "övers."]:
    _exc[orth] = [{ORTH: orth}]


TOKENIZER_EXCEPTIONS = _exc
