# coding: utf8
from __future__ import unicode_literals

import re

# from ._tokenizer_exceptions_list import FR_BASE_EXCEPTIONS
from .punctuation import ELISION, HYPHENS
from ..tokenizer_exceptions import URL_PATTERN
from ..char_classes import ALPHA_LOWER, ALPHA
from ...symbols import ORTH, LEMMA, TAG

# not using the _tokenizer_exceptions_list as hyphens are not used as infix any more
FR_BASE_EXCEPTIONS = ["aujourd'hui", "Aujourd'hui"]


def upper_first_letter(text):
    if len(text) == 0:
        return text
    if len(text) == 1:
        return text.upper()
    return text[0].upper() + text[1:]


def lower_first_letter(text):
    if len(text) == 0:
        return text
    if len(text) == 1:
        return text.lower()
    return text[0].lower() + text[1:]


_exc = {"J.-C.": [{LEMMA: "Jésus", ORTH: "J."}, {LEMMA: "Christ", ORTH: "-C."}]}


for exc_data in [
    {LEMMA: "avant", ORTH: "av."},
    {LEMMA: "janvier", ORTH: "janv."},
    {LEMMA: "février", ORTH: "févr."},
    {LEMMA: "avril", ORTH: "avr."},
    {LEMMA: "juillet", ORTH: "juill."},
    {LEMMA: "septembre", ORTH: "sept."},
    {LEMMA: "octobre", ORTH: "oct."},
    {LEMMA: "novembre", ORTH: "nov."},
    {LEMMA: "décembre", ORTH: "déc."},
    {LEMMA: "après", ORTH: "apr."},
    {LEMMA: "docteur", ORTH: "Dr."},
    {LEMMA: "monsieur", ORTH: "M."},
    {LEMMA: "monsieur", ORTH: "Mr."},
    {LEMMA: "madame", ORTH: "Mme."},
    {LEMMA: "mademoiselle", ORTH: "Mlle."},
    {LEMMA: "numéro", ORTH: "n°"},
    {LEMMA: "degrés", ORTH: "d°"},
    {LEMMA: "saint", ORTH: "St."},
    {LEMMA: "sainte", ORTH: "Ste."},
]:
    _exc[exc_data[ORTH]] = [exc_data]


for orth in ["etc."]:
    _exc[orth] = [{ORTH: orth}]


for verb, verb_lemma in [
    ("a", "avoir"),
    ("est", "être"),
    ("semble", "sembler"),
    ("indique", "indiquer"),
    ("moque", "moquer"),
    ("passe", "passer"),
]:
    for orth in [verb, verb.title()]:
        for pronoun in ["elle", "il", "on"]:
            token = "{}-t-{}".format(orth, pronoun)
            _exc[token] = [
                {LEMMA: verb_lemma, ORTH: orth, TAG: "VERB"},
                {LEMMA: "t", ORTH: "-t"},
                {LEMMA: pronoun, ORTH: "-" + pronoun},
            ]

for verb, verb_lemma in [("est", "être")]:
    for orth in [verb, verb.title()]:
        token = "{}-ce".format(orth)
        _exc[token] = [
            {LEMMA: verb_lemma, ORTH: orth, TAG: "VERB"},
            {LEMMA: "ce", ORTH: "-ce"},
        ]


for pre, pre_lemma in [("qu'", "que"), ("n'", "ne")]:
    for orth in [pre, pre.title()]:
        _exc["%sest-ce" % orth] = [
            {LEMMA: pre_lemma, ORTH: orth, TAG: "ADV"},
            {LEMMA: "être", ORTH: "est", TAG: "VERB"},
            {LEMMA: "ce", ORTH: "-ce"},
        ]


_infixes_exc = []
orig_elision = "'"
orig_hyphen = "-"

# loop through the elison and hyphen characters, and try to substitute the ones that weren't used in the original list
for infix in FR_BASE_EXCEPTIONS:
    variants_infix = {infix}
    for elision_char in [x for x in ELISION if x != orig_elision]:
        variants_infix.update(
            [word.replace(orig_elision, elision_char) for word in variants_infix]
        )
    for hyphen_char in [x for x in ["-", "‐"] if x != orig_hyphen]:
        variants_infix.update(
            [word.replace(orig_hyphen, hyphen_char) for word in variants_infix]
        )
    variants_infix.update([upper_first_letter(word) for word in variants_infix])
    _infixes_exc.extend(variants_infix)

for orth in _infixes_exc:
    _exc[orth] = [{ORTH: orth}]

_regular_exp = [
    "^ch[{elision}]tiis[{al}]+$".format(elision=ELISION, al=ALPHA_LOWER),
    "^droits?[{hyphen}]de[{hyphen}]l'homm[{al}]+$".format(
        hyphen=HYPHENS, al=ALPHA_LOWER
    ),
    "^prud[{elision}]hom[{al}]+$".format(elision=ELISION, al=ALPHA_LOWER),
    "^z[{elision}]yeut[{al}]+$".format(elision=ELISION, al=ALPHA_LOWER),
]

# catching cases like entr'abat
_elision_prefix = ["r?é?entr", "grande?s?", "r"]
_regular_exp += [
    "^{prefix}[{elision}][{al}][{hyphen}{al}{elision}]*$".format(
        prefix=p, elision=ELISION, hyphen=HYPHENS, al=ALPHA_LOWER
    )
    for p in _elision_prefix
]

# catching cases like saut-de-ski, pet-en-l'air
_hyphen_combination = [
    "l[èe]s?",
    "la",
    "en",
    "des?",
    "d[eu]",
    "sur",
    "sous",
    "aux?",
    "à",
    "et",
    "près",
    "saint",
]
_regular_exp += [
    "^[{a}]+[{hyphen}]{hyphen_combo}[{hyphen}](?:l[{elision}])?[{a}]+$".format(
        hyphen_combo=hc, elision=ELISION, hyphen=HYPHENS, a=ALPHA
    )
    for hc in _hyphen_combination
]

# URLs
_regular_exp.append(URL_PATTERN)


TOKENIZER_EXCEPTIONS = _exc
TOKEN_MATCH = re.compile(
    "|".join("(?:{})".format(m) for m in _regular_exp), re.IGNORECASE
).match
