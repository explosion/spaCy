# encoding: utf8
from __future__ import unicode_literals

from ...symbols import ORTH, LEMMA, NORM


_exc = {}

_abbrev_exc = [
    # Weekdays abbreviations
    {ORTH: "пн", LEMMA: "понедельник", NORM: "понедельник"},
    {ORTH: "вт", LEMMA: "вторник", NORM: "вторник"},
    {ORTH: "ср", LEMMA: "среда", NORM: "среда"},
    {ORTH: "чт", LEMMA: "четверг", NORM: "четверг"},
    {ORTH: "чтв", LEMMA: "четверг", NORM: "четверг"},
    {ORTH: "пт", LEMMA: "пятница", NORM: "пятница"},
    {ORTH: "сб", LEMMA: "суббота", NORM: "суббота"},
    {ORTH: "сбт", LEMMA: "суббота", NORM: "суббота"},
    {ORTH: "вс", LEMMA: "воскресенье", NORM: "воскресенье"},
    {ORTH: "вскр", LEMMA: "воскресенье", NORM: "воскресенье"},
    {ORTH: "воскр", LEMMA: "воскресенье", NORM: "воскресенье"},
    # Months abbreviations
    {ORTH: "янв", LEMMA: "январь", NORM: "январь"},
    {ORTH: "фев", LEMMA: "февраль", NORM: "февраль"},
    {ORTH: "февр", LEMMA: "февраль", NORM: "февраль"},
    {ORTH: "мар", LEMMA: "март", NORM: "март"},
    # {ORTH: "март", LEMMA: "март", NORM: "март"},
    {ORTH: "мрт", LEMMA: "март", NORM: "март"},
    {ORTH: "апр", LEMMA: "апрель", NORM: "апрель"},
    # {ORTH: "май", LEMMA: "май", NORM: "май"},
    {ORTH: "июн", LEMMA: "июнь", NORM: "июнь"},
    # {ORTH: "июнь", LEMMA: "июнь", NORM: "июнь"},
    {ORTH: "июл", LEMMA: "июль", NORM: "июль"},
    # {ORTH: "июль", LEMMA: "июль", NORM: "июль"},
    {ORTH: "авг", LEMMA: "август", NORM: "август"},
    {ORTH: "сен", LEMMA: "сентябрь", NORM: "сентябрь"},
    {ORTH: "сент", LEMMA: "сентябрь", NORM: "сентябрь"},
    {ORTH: "окт", LEMMA: "октябрь", NORM: "октябрь"},
    {ORTH: "октб", LEMMA: "октябрь", NORM: "октябрь"},
    {ORTH: "ноя", LEMMA: "ноябрь", NORM: "ноябрь"},
    {ORTH: "нояб", LEMMA: "ноябрь", NORM: "ноябрь"},
    {ORTH: "нбр", LEMMA: "ноябрь", NORM: "ноябрь"},
    {ORTH: "дек", LEMMA: "декабрь", NORM: "декабрь"},
]


for abbrev_desc in _abbrev_exc:
    abbrev = abbrev_desc[ORTH]
    for orth in (abbrev, abbrev.capitalize(), abbrev.upper()):
        _exc[orth] = [{ORTH: orth, LEMMA: abbrev_desc[LEMMA], NORM: abbrev_desc[NORM]}]
        _exc[orth + "."] = [
            {ORTH: orth + ".", LEMMA: abbrev_desc[LEMMA], NORM: abbrev_desc[NORM]}
        ]


_slang_exc = [
    {ORTH: "2к15", LEMMA: "2015", NORM: "2015"},
    {ORTH: "2к16", LEMMA: "2016", NORM: "2016"},
    {ORTH: "2к17", LEMMA: "2017", NORM: "2017"},
    {ORTH: "2к18", LEMMA: "2018", NORM: "2018"},
    {ORTH: "2к19", LEMMA: "2019", NORM: "2019"},
    {ORTH: "2к20", LEMMA: "2020", NORM: "2020"},
]

for slang_desc in _slang_exc:
    _exc[slang_desc[ORTH]] = [slang_desc]


TOKENIZER_EXCEPTIONS = _exc
