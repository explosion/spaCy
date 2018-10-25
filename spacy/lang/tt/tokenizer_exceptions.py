# coding: utf8
from __future__ import unicode_literals

from ...symbols import ORTH, LEMMA, NORM

_exc = {}

_abbrev_exc = [
    # Weekdays abbreviations
    {ORTH: "дш", LEMMA: "дүшәмбе"},
    {ORTH: "сш", LEMMA: "сишәмбе"},
    {ORTH: "чш", LEMMA: "чәршәмбе"},
    {ORTH: "пш", LEMMA: "пәнҗешәмбе"},
    {ORTH: "җм", LEMMA: "җомга"},
    {ORTH: "шб", LEMMA: "шимбә"},
    {ORTH: "яш", LEMMA: "якшәмбе"},

    # Months abbreviations
    {ORTH: "гый", LEMMA: "гыйнвар"},
    {ORTH: "фев", LEMMA: "февраль"},
    {ORTH: "мар", LEMMA: "март"},
    {ORTH: "мар", LEMMA: "март"},
    {ORTH: "апр", LEMMA: "апрель"},
    {ORTH: "июн", LEMMA: "июнь"},
    {ORTH: "июл", LEMMA: "июль"},
    {ORTH: "авг", LEMMA: "август"},
    {ORTH: "сен", LEMMA: "сентябрь"},
    {ORTH: "окт", LEMMA: "октябрь"},
    {ORTH: "ноя", LEMMA: "ноябрь"},
    {ORTH: "дек", LEMMA: "декабрь"},

    # Number abbreviations
    {ORTH: "млрд", LEMMA: "миллиард"},
    {ORTH: "млн", LEMMA: "миллион"},
]

for abbr in _abbrev_exc:
    for orth in (abbr[ORTH], abbr[ORTH].capitalize(), abbr[ORTH].upper()):
        _exc[orth] = [{ORTH: orth, LEMMA: abbr[LEMMA], NORM: abbr[LEMMA]}]
        _exc[orth + "."] = [
            {ORTH: orth + ".", LEMMA: abbr[LEMMA], NORM: abbr[LEMMA]}
        ]

for exc_data in [  # "etc." abbreviations
    {ORTH: "һ.б.ш.", NORM: "һәм башка шундыйлар"},
    {ORTH: "һ.б.", NORM: "һәм башка"},
    {ORTH: "б.э.к.", NORM: "безнең эрага кадәр"},
    {ORTH: "б.э.", NORM: "безнең эра"}]:
    exc_data[LEMMA] = exc_data[NORM]
    _exc[exc_data[ORTH]] = [exc_data]

TOKENIZER_EXCEPTIONS = _exc
