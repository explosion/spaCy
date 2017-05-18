# coding: utf8
from __future__ import unicode_literals

from ..symbols import *

TOKENIZER_EXCEPTIONS = {
    ".i.": [
        {ORTH: ".i.", LEMMA: "eadhon"},
    ],

    "lch.": [
        {ORTH: "lch.", LEMMA: "leathanach"},
    ],

    "lgh.": [
        {ORTH: "lgh.", LEMMA: "leathanaigh"},
    ],

    "m.sh.": [
        {ORTH: "m.", LEMMA: "mar"},
        {ORTH: "sh.", LEMMA: "shampla"}
    ],

    "⁊rl.": [
        {ORTH: "⁊", LEMMA: "agus"},
        {ORTH: "rl.", LEMMA: "araile"}
    ],

    "srl.": [
        {ORTH: "s", LEMMA: "agus"},
        {ORTH: "rl.", LEMMA: "araile"}
    ]

}
