# coding: utf8
from __future__ import unicode_literals

from ._tokenizer_exceptions_list import FR_BASE_EXCEPTIONS

_exc = {}

for orth in FR_BASE_EXCEPTIONS + ["etc."]:
    _exc[orth] = [{ORTH: orth}]

TOKENIZER_EXCEPTIONS = dict(_exc)