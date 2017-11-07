# coding: utf8
from __future__ import unicode_literals

from ...symbols import LEMMA, PRON_LEMMA


MORPH_RULES = {
    "PRON": {
        "jeg":            {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Sing", "Case": "Nom"},
        "mig":           {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Sing", "Case": "Acc"},
        "du":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Two"},
        "han":           {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Gender": "Masc", "Case": "Nom"},
        "ham":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Gender": "Masc", "Case": "Acc"},
        "hun":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Gender": "Fem",  "Case": "Nom"},
        "hende":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Gender": "Fem",  "Case": "Acc"},
        "den":           {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Gender": "Neut"},
        "det":           {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Gender": "Neut"},
        "vi":           {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Plur", "Case": "Nom"},
        "os":           {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Plur", "Case": "Acc"},
        "de":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Plur", "Case": "Nom"},
        "dem":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Plur", "Case": "Acc"},

        "min":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Sing", "Poss": "Yes", "Reflex": "Yes"},
        "din":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Two", "Number": "Sing", "Poss": "Yes", "Reflex": "Yes"},
        "hans":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Gender": "Masc", "Poss": "Yes", "Reflex": "Yes"},
        "hendes":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Gender": "Fem",  "Poss": "Yes", "Reflex": "Yes"},
        "dens":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Gender": "Neut", "Poss": "Yes", "Reflex": "Yes"},
        "dets":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Gender": "Neut", "Poss": "Yes", "Reflex": "Yes"},
        "vores":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Plur", "Poss": "Yes", "Reflex": "Yes"},
        "deres":       {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Plur", "Poss": "Yes", "Reflex": "Yes"},
    },

    "VERB": {
        "er":           {LEMMA: "være", "VerbForm": "Fin", "Tense": "Pres"},
        "var":          {LEMMA: "være", "VerbForm": "Fin", "Tense": "Past"}
    }
}

for tag, rules in MORPH_RULES.items():
    for key, attrs in dict(rules).items():
        rules[key.title()] = attrs
