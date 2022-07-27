from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...symbols import ORTH
from ...util import update_exc


_exc = {
    "mecum": [{ORTH: "me"}, {ORTH: "cum"}],
}

for orth in [
    "Kal.",
]:
    _exc[orth] = [{ORTH: orth}]

TOKENIZER_EXCEPTIONS = update_exc(BASE_EXCEPTIONS, _exc)
