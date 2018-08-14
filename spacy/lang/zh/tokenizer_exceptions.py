# encoding: utf8
from __future__ import unicode_literals

from ...symbols import *


TOKENIZER_EXCEPTIONS = {
    "Jan.": [
        {ORTH: "Jan.", LEMMA: "January"}
    ]
}


# exceptions mapped to a single token containing only ORTH property
# example: {"string": [{ORTH: "string"}]}
# converted using strings_to_exc() util

ORTH_ONLY = [
    "a.",
    "b.",
    "c.",
    "d.",
    "e.",
    "f.",
    "g.",
    "h.",
    "i.",
    "j.",
    "k.",
    "l.",
    "m.",
    "n.",
    "o.",
    "p.",
    "q.",
    "r.",
    "s.",
    "t.",
    "u.",
    "v.",
    "w.",
    "x.",
    "y.",
    "z."
]
