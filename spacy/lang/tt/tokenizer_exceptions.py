from ...symbols import NORM, ORTH
from ...util import update_exc
from ..tokenizer_exceptions import BASE_EXCEPTIONS

_exc = {}

_abbrev_exc = [
    # Weekdays abbreviations
    {ORTH: "дш", NORM: "дүшәмбе"},
    {ORTH: "сш", NORM: "сишәмбе"},
    {ORTH: "чш", NORM: "чәршәмбе"},
    {ORTH: "пш", NORM: "пәнҗешәмбе"},
    {ORTH: "җм", NORM: "җомга"},
    {ORTH: "шб", NORM: "шимбә"},
    {ORTH: "яш", NORM: "якшәмбе"},
    # Months abbreviations
    {ORTH: "гый", NORM: "гыйнвар"},
    {ORTH: "фев", NORM: "февраль"},
    {ORTH: "мар", NORM: "март"},
    {ORTH: "мар", NORM: "март"},
    {ORTH: "апр", NORM: "апрель"},
    {ORTH: "июн", NORM: "июнь"},
    {ORTH: "июл", NORM: "июль"},
    {ORTH: "авг", NORM: "август"},
    {ORTH: "сен", NORM: "сентябрь"},
    {ORTH: "окт", NORM: "октябрь"},
    {ORTH: "ноя", NORM: "ноябрь"},
    {ORTH: "дек", NORM: "декабрь"},
    # Number abbreviations
    {ORTH: "млрд", NORM: "миллиард"},
    {ORTH: "млн", NORM: "миллион"},
]

for abbr in _abbrev_exc:
    for orth in (abbr[ORTH], abbr[ORTH].capitalize(), abbr[ORTH].upper()):
        _exc[orth] = [{ORTH: orth, NORM: abbr[NORM]}]
        _exc[orth + "."] = [{ORTH: orth + ".", NORM: abbr[NORM]}]

for exc_data in [  # "etc." abbreviations
    {ORTH: "һ.б.ш.", NORM: "һәм башка шундыйлар"},
    {ORTH: "һ.б.", NORM: "һәм башка"},
    {ORTH: "б.э.к.", NORM: "безнең эрага кадәр"},
    {ORTH: "б.э.", NORM: "безнең эра"},
]:
    _exc[exc_data[ORTH]] = [exc_data]

TOKENIZER_EXCEPTIONS = update_exc(BASE_EXCEPTIONS, _exc)
