from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...symbols import ORTH, NORM
from ...util import update_exc


_exc = {}

for exc_data in [
    {ORTH: "aprox.", NORM: "aproximadament"},
    {ORTH: "pàg.", NORM: "pàgina"},
    {ORTH: "p.ex.", NORM: "per exemple"},
    {ORTH: "gen.", NORM: "gener"},
    {ORTH: "feb.", NORM: "febrer"},
    {ORTH: "abr.", NORM: "abril"},
    {ORTH: "jul.", NORM: "juliol"},
    {ORTH: "set.", NORM: "setembre"},
    {ORTH: "oct.", NORM: "octubre"},
    {ORTH: "nov.", NORM: "novembre"},
    {ORTH: "dec.", NORM: "desembre"},
    {ORTH: "Dr.", NORM: "doctor"},
    {ORTH: "Dra.", NORM: "doctora"},
    {ORTH: "Sr.", NORM: "senyor"},
    {ORTH: "Sra.", NORM: "senyora"},
    {ORTH: "Srta.", NORM: "senyoreta"},
    {ORTH: "núm", NORM: "número"},
    {ORTH: "St.", NORM: "sant"},
    {ORTH: "Sta.", NORM: "santa"},
    {ORTH: "pl.", NORM: "plaça"},
    {ORTH: "à."},
    {ORTH: "è."},
    {ORTH: "é."},
    {ORTH: "í."},
    {ORTH: "ò."},
    {ORTH: "ó."},
    {ORTH: "ú."},
    {ORTH: "'l"},
    {ORTH: "'ls"},
    {ORTH: "'m"},
    {ORTH: "'n"},
    {ORTH: "'ns"},
    {ORTH: "'s"},
    {ORTH: "'t"},
]:
    _exc[exc_data[ORTH]] = [exc_data]

_exc["del"] = [{ORTH: "d", NORM: "de"}, {ORTH: "el"}]
_exc["dels"] = [{ORTH: "d", NORM: "de"}, {ORTH: "els"}]

_exc["al"] = [{ORTH: "a"}, {ORTH: "l", NORM: "el"}]
_exc["als"] = [{ORTH: "a"}, {ORTH: "ls", NORM: "els"}]

_exc["pel"] = [{ORTH: "p", NORM: "per"}, {ORTH: "el"}]
_exc["pels"] = [{ORTH: "p", NORM: "per"}, {ORTH: "els"}]

_exc["holahola"] = [{ORTH: "holahola", NORM: "cocacola"}]


# Times
_exc["12m."] = [{ORTH: "12"}, {ORTH: "m.", NORM: "p.m."}]

for h in range(1, 12 + 1):
    for period in ["a.m.", "am"]:
        _exc[f"{h}{period}"] = [{ORTH: f"{h}"}, {ORTH: period, NORM: "a.m."}]
    for period in ["p.m.", "pm"]:
        _exc[f"{h}{period}"] = [{ORTH: f"{h}"}, {ORTH: period, NORM: "p.m."}]


TOKENIZER_EXCEPTIONS = update_exc(BASE_EXCEPTIONS, _exc)
