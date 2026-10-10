from ...symbols import ORTH
from ...util import update_exc
from ..tokenizer_exceptions import BASE_EXCEPTIONS

_exc = {}

# Mixed Urdu-English news text commonly keeps these Latin abbreviations intact.
for orth in [
    "Dr.",
    "Mr.",
    "Mrs.",
    "Ms.",
    "Prof.",
    "vs.",
    "etc.",
    "i.e.",
    "e.g.",
    "U.S.",
    "U.K.",
    "U.N.",
]:
    _exc[orth] = [{ORTH: orth}]

# Postal / reference abbreviation used in Urdu and Arabic.
_exc["ص.ب"] = [{ORTH: "ص.ب"}]

TOKENIZER_EXCEPTIONS = update_exc(BASE_EXCEPTIONS, _exc)
