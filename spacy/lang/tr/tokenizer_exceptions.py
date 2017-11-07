# coding: utf8
from __future__ import unicode_literals

from ...symbols import ORTH, NORM


# These exceptions are mostly for example purposes – hoping that Turkish
# speakers can contribute in the future! Source of copy-pasted examples:
# https://en.wiktionary.org/wiki/Category:Turkish_language

_exc = {
    "sağol": [
        {ORTH: "sağ"},
        {ORTH: "ol", NORM: "olun"}]
}


for exc_data in [
    {ORTH: "A.B.D.", NORM: "Amerika Birleşik Devletleri"}]:
    _exc[exc_data[ORTH]] = [exc_data]


for orth in ["Dr."]:
    _exc[orth] = [{ORTH: orth}]


TOKENIZER_EXCEPTIONS = _exc
