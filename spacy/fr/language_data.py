# encoding: utf8
from __future__ import unicode_literals

from .. import language_data as base
from ..language_data import strings_to_exc, update_exc

from .punctuation import ELISION

from ..symbols import *
from .stop_words import STOP_WORDS


STOP_WORDS = set(STOP_WORDS)


TOKENIZER_EXCEPTIONS = strings_to_exc(base.EMOTICONS)
update_exc(TOKENIZER_EXCEPTIONS, strings_to_exc(base.ABBREVIATIONS))

ABBREVIATIONS = {
    "janv.": [
        {LEMMA: "janvier", ORTH: "janv."}
    ],
    "févr.": [
        {LEMMA: "février", ORTH: "févr."}
    ],
    "avr.": [
        {LEMMA: "avril", ORTH: "avr."}
    ],
    "juill.": [
        {LEMMA: "juillet", ORTH: "juill."}
    ],
    "sept.": [
        {LEMMA: "septembre", ORTH: "sept."}
    ],
    "oct.": [
        {LEMMA: "octobre", ORTH: "oct."}
    ],
    "nov.": [
        {LEMMA: "novembre", ORTH: "nov."}
    ],
    "déc.": [
        {LEMMA: "décembre", ORTH: "déc."}
    ],
    "av.": [
        {LEMMA: "avant", ORTH: "av."}
    ],
    "apr.": [
        {LEMMA: "après", ORTH: "apr."}
    ],
    "J.-C.": [
        {LEMMA: "jésus", ORTH: "J."},
        {LEMMA: "christ", ORTH: "-C."}
    ],
    "Dr.": [
        {LEMMA: "docteur", ORTH: "Dr."}
    ],
    "M.": [
        {LEMMA: "monsieur", ORTH: "M."}
    ],
    "Mr.": [
        {LEMMA: "monsieur", ORTH: "Mr."}
    ],
    "Mme.": [
        {LEMMA: "madame", ORTH: "Mme."}
    ],
    "Mlle.": [
        {LEMMA: "mademoiselle", ORTH: "Mlle."}
    ],
    "n°": [
        {LEMMA: "numéro", ORTH: "n°"}
    ],
    "d°": [
        {LEMMA: "degrés", ORTH: "d°"}
    ],
    "St.": [
        {LEMMA: "saint", ORTH: "St."}
    ],
    "Ste.": [
        {LEMMA: "sainte", ORTH: "Ste."}
    ]
}


INFIXES_EXCEPTIONS_BASE = ["aujourd'hui",
                           "prud'homme", "prud'hommes",
                           "prud'homal", "prud'homaux", "prud'homale",
                           "prud'homales",
                           "prud'hommal", "prud'hommaux", "prud'hommale",
                           "prud'hommales",
                           "prud'homie", "prud'homies",
                           "prud'hommesque", "prud'hommesques",
                           "prud'hommesquement",
                           "c'est-à-dire", "quelqu'un", "rendez-vous"]

INFIXES_EXCEPTIONS = []
for elision_char in ELISION:
    INFIXES_EXCEPTIONS += [infix.replace("'", elision_char)
                           for infix in INFIXES_EXCEPTIONS_BASE]

INFIXES_EXCEPTIONS += [word.capitalize() for word in INFIXES_EXCEPTIONS]

update_exc(TOKENIZER_EXCEPTIONS, strings_to_exc(INFIXES_EXCEPTIONS))
update_exc(TOKENIZER_EXCEPTIONS, ABBREVIATIONS)


__all__ = ["TOKENIZER_EXCEPTIONS", "STOP_WORDS"]
