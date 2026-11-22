from ...symbols import NORM, ORTH
from ...util import update_exc
from ..tokenizer_exceptions import BASE_EXCEPTIONS

_exc = {}

for exc_data in [
    {ORTH: "e.e.", NORM: "er enghraifft"},
    {ORTH: "h.y.", NORM: "hynny yw"},
    {ORTH: "a.y.b.", NORM: "ac yn y blaen"},
    {ORTH: "Dr.", NORM: "Doctor"},
    {ORTH: "Mr.", NORM: "Mister"},
    {ORTH: "Mrs.", NORM: "Missus"},
]:
    _exc[exc_data[ORTH]] = [exc_data]

# A clitic standing on its own (after a space, or once split off by the
# suffix rules) must not lose its apostrophe to the quote prefix rule.
for clitic in ["r", "n", "i", "m", "ch", "th", "u", "w"]:
    for apostrophe in ["'", "’"]:
        for form in [clitic, clitic.upper()]:
            orth = apostrophe + form
            _exc[orth] = [{ORTH: orth}]

TOKENIZER_EXCEPTIONS = update_exc(BASE_EXCEPTIONS, _exc)
