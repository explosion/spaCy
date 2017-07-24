# coding: utf8
from __future__ import unicode_literals

from ._tokenizer_exceptions_list import ID_BASE_EXCEPTIONS
from ...symbols import ORTH

_exc = {}

for orth in ID_BASE_EXCEPTIONS + ["etc."]:
    _exc[orth] = [{ORTH: orth}]

TOKENIZER_EXCEPTIONS = dict(_exc)