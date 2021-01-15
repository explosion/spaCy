from ...symbols import ORTH, NORM


_exc = {}


for exc_data in [
    {ORTH: "ት/ቤት"},
    {ORTH: "ወ/ሮ", NORM: "ወይዘሮ"},
    {ORTH: "ወ/ሪ", NORM: "ወይዘሪት"},
]:
    _exc[exc_data[ORTH]] = [exc_data]


for orth in [
    "ዓ.ም.",
    "ኪ.ሜ.",
]:
    _exc[orth] = [{ORTH: orth}]


TOKENIZER_EXCEPTIONS = _exc
