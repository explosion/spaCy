# coding: utf8
from __future__ import unicode_literals

from ...symbols import ORTH, NORM

TOKENIZER_EXCEPTIONS = {
    "wedi'i": [
        {ORTH: "wedi"},
        {ORTH: "'i", NORM: "ei"}]
}
