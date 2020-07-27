from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...symbols import ORTH, NORM
from ...util import update_exc


_exc = {}

for exc_data in [
    {ORTH: "вул.", NORM: "вулиця"},
    {ORTH: "ім.", NORM: "імені"},
    {ORTH: "просп.", NORM: "проспект"},
    {ORTH: "бул.", NORM: "бульвар"},
    {ORTH: "пров.", NORM: "провулок"},
    {ORTH: "пл.", NORM: "площа"},
    {ORTH: "г.", NORM: "гора"},
    {ORTH: "п.", NORM: "пан"},
    {ORTH: "м.", NORM: "місто"},
    {ORTH: "проф.", NORM: "професор"},
    {ORTH: "акад.", NORM: "академік"},
    {ORTH: "доц.", NORM: "доцент"},
    {ORTH: "оз.", NORM: "озеро"},
]:
    _exc[exc_data[ORTH]] = [exc_data]


TOKENIZER_EXCEPTIONS = update_exc(BASE_EXCEPTIONS, _exc)
