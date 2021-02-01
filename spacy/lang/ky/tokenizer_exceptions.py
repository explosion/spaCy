# coding: utf8
from __future__ import unicode_literals

from ...symbols import ORTH, LEMMA, NORM

_exc = {}

_abbrev_exc = [
    # Weekdays abbreviations
    {ORTH: "дүй", LEMMA: "дүйшөмбү"},
    {ORTH: "шей", LEMMA: "шейшемби"},
    {ORTH: "шар", LEMMA: "шаршемби"},
    {ORTH: "бей", LEMMA: "бейшемби"},
    {ORTH: "жум", LEMMA: "жума"},
    {ORTH: "ишм", LEMMA: "ишемби"},
    {ORTH: "жек", LEMMA: "жекшемби"},
    # Months abbreviations
    {ORTH: "янв", LEMMA: "январь"},
    {ORTH: "фев", LEMMA: "февраль"},
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
        _exc[orth + "."] = [{ORTH: orth + ".", LEMMA: abbr[LEMMA], NORM: abbr[LEMMA]}]

for exc_data in [  # "etc." abbreviations
    {ORTH: "ж.б.у.с.", NORM: "жана башка ушул сыяктуу"},
    {ORTH: "ж.б.", NORM: "жана башка"},
    {ORTH: "ж.", NORM: "жыл"},
    {ORTH: "б.з.ч.", NORM: "биздин заманга чейин"},
    {ORTH: "б.з.", NORM: "биздин заман"},
    {ORTH: "кк.", NORM: "кылымдар"},
    {ORTH: "жж.", NORM: "жылдар"},
    {ORTH: "к.", NORM: "кылым"},
    {ORTH: "көч.", NORM: "көчөсү"},
    {ORTH: "м-н", NORM: "менен"},
    {ORTH: "б-ча", NORM: "боюнча"},
]:
    exc_data[LEMMA] = exc_data[NORM]
    _exc[exc_data[ORTH]] = [exc_data]

TOKENIZER_EXCEPTIONS = _exc
