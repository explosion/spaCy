# coding: utf8
from __future__ import unicode_literals

from ..symbols import *
from ..language_data import PRON_LEMMA

TOKENIZER_EXCEPTIONS = {}

# Contractions
CONTRACTIONS = {}

personal_pronoun = (
    "ele", "ela", "eles", "elas"
)
demonstrative_pronouns = (
    "este", "esta", "estes", "estas", "isto", "esse", "essa", "esses", "essas",
    "isso", "aquele", "aquela", "aqueles", "aquelas", "aquilo"
)
undefined_pronouns = (
    "outro", "outra", "outros", "outras"
)
adverbs = (
    "aqui", "aí", "ali", "além"
)

for word in personal_pronoun + demonstrative_pronouns + \
            undefined_pronouns + adverbs:
    CONTRACTIONS["d" + word] = [
        {ORTH: "d", NORM: "de"},
        {ORTH: word}
    ]

for word in personal_pronoun + demonstrative_pronouns + \
            undefined_pronouns:
    CONTRACTIONS["n" + word] = [
        {ORTH: "n", NORM: "em"},
        {ORTH: word}
    ]

# Not so linear contractions "a"+something

CONTRACTIONS.update({
    # This one cannot be split into 2
    # "à": [
    #     {ORTH: "à", NORM: "a"},
    #     {ORTH: "", NORM: "a"}
    # ],
    "às": [
        {ORTH: "à", NORM: "a"},
        {ORTH: "s", NORM: "as"}
    ],
    "ao": [
        {ORTH: "a"},
        {ORTH: "o"}
    ],
    "aos": [
        {ORTH: "a"},
        {ORTH: "os"}
    ],
    "àquele": [
        {ORTH: "à", NORM: "a"},
        {ORTH: "quele", NORM: "aquele"}
    ],
    "àquela": [
        {ORTH: "à", NORM: "a"},
        {ORTH: "quela", NORM: "aquela"}
    ],
    "àqueles": [
        {ORTH: "à", NORM: "a"},
        {ORTH: "queles", NORM: "aqueles"}
    ],
    "àquelas": [
        {ORTH: "à", NORM: "a"},
        {ORTH: "quelas", NORM: "aquelas"}
    ],
    "àquilo": [
        {ORTH: "à", NORM: "a"},
        {ORTH: "quilo", NORM: "aquilo"}
    ],
    "aonde": [
        {ORTH: "a"},
        {ORTH: "onde"}
    ],
})

TOKENIZER_EXCEPTIONS.update(CONTRACTIONS)

# Abbreviations with only one ORTH token

ORTH_ONLY = [
    "Adm.",
    "Dr.",
    "e.g.",
    "E.g.",
    "E.G.",
    "Gen.",
    "Gov.",
    "i.e.",
    "I.e.",
    "I.E.",
    "Jr.",
    "Ltd.",
    "p.m.",
    "Ph.D.",
    "Rep.",
    "Rev.",
    "Sen.",
    "Sr.",
    "Sra.",
    "vs.",
]
