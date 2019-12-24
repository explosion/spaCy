# encoding: utf8
from __future__ import unicode_literals

from ..symbols import *
from ..language_data import PRON_LEMMA


TOKENIZER_EXCEPTIONS = {
    "ม.ค.": [
        {ORTH: "ม.ค.", LEMMA: "มกราคม"}
    ],
    "ก.พ.": [
        {ORTH: "ก.พ.", LEMMA: "กุมภาพันธ์"}
    ],
    "มี.ค.": [
        {ORTH: "มี.ค.", LEMMA: "มีนาคม"}
    ],
    "เม.ย.": [
        {ORTH: "เม.ย.", LEMMA: "เมษายน"}
    ],
    "พ.ค.": [
        {ORTH: "พ.ค.", LEMMA: "พฤษภาคม"}
    ],
    "มิ.ย.": [
        {ORTH: "มิ.ย.", LEMMA: "มิถุนายน"}
    ],
    "ก.ค.": [
        {ORTH: "ก.ค.", LEMMA: "กรกฎาคม"}
    ],
    "ส.ค.": [
        {ORTH: "ส.ค.", LEMMA: "สิงหาคม"}
    ],
    "ก.ย.": [
        {ORTH: "ก.ย.", LEMMA: "กันยายน"}
    ],
    "ต.ค.": [
        {ORTH: "ต.ค.", LEMMA: "ตุลาคม"}
    ],
    "พ.ย.": [
        {ORTH: "พ.ย.", LEMMA: "พฤศจิกายน"}
    ],
    "ธ.ค.": [
        {ORTH: "ธ.ค.", LEMMA: "ธันวาคม"}
    ]
}


# exceptions mapped to a single token containing only ORTH property
# example: {"string": [{ORTH: "string"}]}
# converted using strings_to_exc() util
'''
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
'''