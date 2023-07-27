from ...symbols import NORM, ORTH
from ...util import update_exc
from ..tokenizer_exceptions import BASE_EXCEPTIONS

_exc = {}

for exc_data in [
    {ORTH: "обл.", NORM: "область"},
    {ORTH: "р-н.", NORM: "район"},
    {ORTH: "р-н", NORM: "район"},
    {ORTH: "м.", NORM: "місто"},
    {ORTH: "вул.", NORM: "вулиця"},
    {ORTH: "просп.", NORM: "проспект"},
    {ORTH: "пр-кт", NORM: "проспект"},
    {ORTH: "бул.", NORM: "бульвар"},
    {ORTH: "пров.", NORM: "провулок"},
    {ORTH: "пл.", NORM: "площа"},
    {ORTH: "майд.", NORM: "майдан"},
    {ORTH: "мкр.", NORM: "мікрорайон"},
    {ORTH: "ст.", NORM: "станція"},
    {ORTH: "ж/м", NORM: "житловий масив"},
    {ORTH: "наб.", NORM: "набережна"},
    {ORTH: "в/ч", NORM: "військова частина"},
    {ORTH: "в/м", NORM: "військове містечко"},
    {ORTH: "оз.", NORM: "озеро"},
    {ORTH: "ім.", NORM: "імені"},
    {ORTH: "г.", NORM: "гора"},
    {ORTH: "п.", NORM: "пан"},
    {ORTH: "проф.", NORM: "професор"},
    {ORTH: "акад.", NORM: "академік"},
    {ORTH: "доц.", NORM: "доцент"},
]:
    _exc[exc_data[ORTH]] = [exc_data]


TOKENIZER_EXCEPTIONS = update_exc(BASE_EXCEPTIONS, _exc)
