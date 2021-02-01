from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...symbols import ORTH, NORM
from ...util import update_exc

_exc = {}

_abbrev_exc = [
    # Weekdays abbreviations
    {ORTH: "дүй", NORM: "дүйшөмбү"},
    {ORTH: "шей", NORM: "шейшемби"},
    {ORTH: "шар", NORM: "шаршемби"},
    {ORTH: "бей", NORM: "бейшемби"},
    {ORTH: "жум", NORM: "жума"},
    {ORTH: "ишм", NORM: "ишемби"},
    {ORTH: "жек", NORM: "жекшемби"},
    # Months abbreviations
    {ORTH: "янв", NORM: "январь"},
    {ORTH: "фев", NORM: "февраль"},
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
    _exc[exc_data[ORTH]] = [exc_data]

TOKENIZER_EXCEPTIONS = update_exc(BASE_EXCEPTIONS, _exc)
