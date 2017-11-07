# coding: utf8
from __future__ import unicode_literals

from ...symbols import ORTH


_exc = {}


# Source: https://en.wiktionary.org/wiki/Category:Romanian_abbreviations
for orth in [
    "1-a", "1-ul", "10-a", "10-lea", "2-a", "3-a", "3-lea", "6-lea",
    "d-voastră", "dvs.", "Rom.", "str."]:
    _exc[orth] = [{ORTH: orth}]


TOKENIZER_EXCEPTIONS = _exc
