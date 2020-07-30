# coding: utf8
from __future__ import unicode_literals

from ...symbols import ORTH, LEMMA, TAG, NORM, PRON_LEMMA

# Hindi Pronoun: https://en.wiktionary.org/wiki/Category:Hindi_pronouns
# https://hi.wikipedia.org/wiki/कारक 

_exc = {
    "मैंने": [
        {ORTH: "मैं", LEMMA: PRON_LEMMA, NORM: "मैं"},
        {ORTH: "ने", LEMMA: "ने", NORM: "ने"},
    ],
    "आपको":[
        {ORTH: "आप", LEMMA: PRON_LEMMA, NORM: "आप"},
        {ORTH: "को", LEMMA: "को", NORM: "को"},
    ]
} 


TOKENIZER_EXCEPTIONS = _exc
