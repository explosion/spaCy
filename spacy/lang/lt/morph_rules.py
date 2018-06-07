# coding: utf8
from __future__ import unicode_literals

from ...symbols import LEMMA, PRON_LEMMA


MORPH_RULES = {
    "PRP": {
        "aš":           {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Sing"},
        "tu":           {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Two"},
        "jis":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Gender": "Masc", "Case": "Nom"},
        "jam":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Gender": "Masc", "Case": "Acc"},
        "ji":           {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Gender": "Fem",  "Case": "Nom"},
        "jai":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Gender": "Fem",  "Case": "Acc"},
        "mes":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Plur", "Case": "Nom"},
        "mus":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Plur", "Case": "Acc"},
        "jie":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Plur", "Case": "Nom"},
        "jiems":        {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Plur", "Case": "Acc"},

        "mano":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Sing", "Poss": "Yes", "Reflex": "Yes"},
        "jo":           {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Gender": "Masc", "Poss": "Yes", "Reflex": "Yes"},
        "jos":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Gender": "Fem",  "Poss": "Yes", "Reflex": "Yes"},
        "mūsų":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Plur", "Poss": "Yes", "Reflex": "Yes"},
        "jūsų":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Two", "Number": "Plur", "Poss": "Yes", "Reflex": "Yes"},
        "jų":           {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Plur", "Poss": "Yes", "Reflex": "Yes"},

        "sau":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Case": "Acc", "Reflex": "Yes"},
    },

    "PRP$": {
        "mano":         {LEMMA: PRON_LEMMA, "Person": "One", "Number": "Sing", "PronType": "Prs", "Poss": "Yes"},
        "tavo":         {LEMMA: PRON_LEMMA, "Person": "Two", "PronType": "Prs", "Poss": "Yes"},
        "jo":           {LEMMA: PRON_LEMMA, "Person": "Three", "Number": "Sing", "Gender": "Masc", "PronType": "Prs", "Poss": "Yes"},
        "jos":          {LEMMA: PRON_LEMMA, "Person": "Three", "Number": "Sing", "Gender": "Fem",  "PronType": "Prs", "Poss": "Yes"},
        "mūsų":         {LEMMA: PRON_LEMMA, "Person": "One", "Number": "Plur", "PronType": "Prs", "Poss": "Yes"},
        "jų":           {LEMMA: PRON_LEMMA, "Person": "Three", "Number": "Plur", "PronType": "Prs", "Poss": "Yes"}
    },

    "VBZ": {
        "esu":          {LEMMA: "būti", "VerbForm": "Fin", "Person": "One", "Tense": "Pres", "Mood": "Ind"},
        "esi":          {LEMMA: "būti", "VerbForm": "Fin", "Person": "Two", "Tense": "Pres", "Mood": "Ind"},
        "yra":          {LEMMA: "būti", "VerbForm": "Fin", "Person": "Three", "Tense": "Pres", "Mood": "Ind"},
    },

    "VBP": {
        "yra":          {LEMMA: "būti", "VerbForm": "Fin", "Tense": "Pres", "Mood": "Ind"},
        "esu":          {LEMMA: "būti", "VerbForm": "Fin", "Person": "One", "Tense": "Pres", "Mood": "Ind"},
    },

    "VBD": {
        "buvo":         {LEMMA: "būti", "VerbForm": "Fin", "Tense": "Past"},
        "buvau":        {LEMMA: "būti", "VerbForm": "Fin", "Tense": "Past", "Person": "One"}
    }
}


for tag, rules in MORPH_RULES.items():
    for key, attrs in dict(rules).items():
        rules[key.title()] = attrs
