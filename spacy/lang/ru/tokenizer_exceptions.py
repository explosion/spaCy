from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...symbols import ORTH, NORM
from ...util import update_exc


_exc = {}

_abbrev_exc = [
    # Weekdays abbreviations
    {ORTH: "пн", NORM: "понедельник"},
    {ORTH: "вт", NORM: "вторник"},
    {ORTH: "ср", NORM: "среда"},
    {ORTH: "чт", NORM: "четверг"},
    {ORTH: "чтв", NORM: "четверг"},
    {ORTH: "пт", NORM: "пятница"},
    {ORTH: "сб", NORM: "суббота"},
    {ORTH: "сбт", NORM: "суббота"},
    {ORTH: "вс", NORM: "воскресенье"},
    {ORTH: "вскр", NORM: "воскресенье"},
    {ORTH: "воскр", NORM: "воскресенье"},
    # Months abbreviations
    {ORTH: "янв", NORM: "январь"},
    {ORTH: "фев", NORM: "февраль"},
    {ORTH: "февр", NORM: "февраль"},
    {ORTH: "мар", NORM: "март"},
    # {ORTH: "март", NORM: "март"},
    {ORTH: "мрт", NORM: "март"},
    {ORTH: "апр", NORM: "апрель"},
    # {ORTH: "май", NORM: "май"},
    {ORTH: "июн", NORM: "июнь"},
    # {ORTH: "июнь", NORM: "июнь"},
    {ORTH: "июл", NORM: "июль"},
    # {ORTH: "июль", NORM: "июль"},
    {ORTH: "авг", NORM: "август"},
    {ORTH: "сен", NORM: "сентябрь"},
    {ORTH: "сент", NORM: "сентябрь"},
    {ORTH: "окт", NORM: "октябрь"},
    {ORTH: "октб", NORM: "октябрь"},
    {ORTH: "ноя", NORM: "ноябрь"},
    {ORTH: "нояб", NORM: "ноябрь"},
    {ORTH: "нбр", NORM: "ноябрь"},
    {ORTH: "дек", NORM: "декабрь"},
]


for abbrev_desc in _abbrev_exc:
    abbrev = abbrev_desc[ORTH]
    for orth in (abbrev, abbrev.capitalize(), abbrev.upper()):
        _exc[orth] = [{ORTH: orth, NORM: abbrev_desc[NORM]}]
        _exc[orth + "."] = [{ORTH: orth + ".", NORM: abbrev_desc[NORM]}]


_slang_exc = [
    {ORTH: "2к15", NORM: "2015"},
    {ORTH: "2к16", NORM: "2016"},
    {ORTH: "2к17", NORM: "2017"},
    {ORTH: "2к18", NORM: "2018"},
    {ORTH: "2к19", NORM: "2019"},
    {ORTH: "2к20", NORM: "2020"},
]

for slang_desc in _slang_exc:
    _exc[slang_desc[ORTH]] = [slang_desc]


TOKENIZER_EXCEPTIONS = update_exc(BASE_EXCEPTIONS, _exc)
