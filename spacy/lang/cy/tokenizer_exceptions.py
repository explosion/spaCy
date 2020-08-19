# coding: utf8
from ...symbols import ORTH, NORM

TOKENIZER_EXCEPTIONS = {
    "wedi'i": [
        {ORTH: "wedi"},
        {ORTH: "'i", NORM: "ei"}]
}
