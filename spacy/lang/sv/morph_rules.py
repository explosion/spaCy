# coding: utf8
from __future__ import unicode_literals

from ...symbols import LEMMA, PRON_LEMMA


# Used the table of pronouns at https://sv.wiktionary.org/wiki/deras

MORPH_RULES = {
    "PRP": {
        "jag":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Sing", "Case": "Nom"},
        "mig":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Sing", "Case": "Acc"},
        "mej":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Sing", "Case": "Acc"},
        "du":           {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Two", "Number": "Sing", "Case": "Nom"},
        "han":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Gender": "Masc", "Case": "Nom"},
        "honom":        {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Gender": "Masc", "Case": "Acc"},
        "hon":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Gender": "Fem",  "Case": "Nom"},
        "henne":        {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Gender": "Fem",  "Case": "Acc"},
        "det":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Gender": "Neut"},
        "vi":           {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Plur", "Case": "Nom"},
        "oss":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Plur", "Case": "Acc"},
        "ni":           {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Two", "Number": "Plur", "Case": "Nom"},
        "er":           {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Two", "Number": "Plur", "Case": "Acc"},
        "de":           {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Plur", "Case": "Nom"},
        "dom":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Plur", "Case": "Nom"},
        "dem":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Plur", "Case": "Acc"},
        "dom":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Plur", "Case": "Acc"},

        "min":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Sing", "Poss": "Yes", "Reflex": "Yes"},
        "mitt":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Sing", "Poss": "Yes", "Reflex": "Yes"},
        "mina":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Plur", "Poss": "Yes", "Reflex": "Yes"},
        "din":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Two", "Number": "Sing", "Poss": "Yes", "Reflex": "Yes"},
        "ditt":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Two", "Number": "Sing", "Poss": "Yes", "Reflex": "Yes"},
        "dina":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Two", "Number": "Plur", "Poss": "Yes", "Reflex": "Yes"},
        "hans":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Two", "Number": "Sing", "Gender": "Masc", "Poss": "Yes", "Reflex": "Yes"},
        "hans":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Two", "Number": "Plur", "Gender": "Masc", "Poss": "Yes", "Reflex": "Yes"},
        "hennes":       {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Two", "Number": "Sing", "Gender": "Fem", "Poss": "Yes", "Reflex": "Yes"},
        "hennes":       {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Two", "Number": "Plur", "Gender": "Fem", "Poss": "Yes", "Reflex": "Yes"},
        "dess":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Two", "Number": "Sing", "Poss": "Yes", "Reflex": "Yes"},
        "dess":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Two", "Number": "Plur", "Poss": "Yes", "Reflex": "Yes"},
        "vår":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Plur", "Poss": "Yes", "Reflex": "Yes"},
        "våran":        {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Plur", "Poss": "Yes", "Reflex": "Yes"},
        "vårt":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Plur", "Poss": "Yes", "Reflex": "Yes"},
        "vårat":        {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Plur", "Poss": "Yes", "Reflex": "Yes"},
        "våra":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Plur", "Poss": "Yes", "Reflex": "Yes"},
        "er":           {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Two", "Number": "Plur", "Poss": "Yes", "Reflex": "Yes"},
        "eran":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Two", "Number": "Plur", "Poss": "Yes", "Reflex": "Yes"},
        "ert":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Two", "Number": "Plur", "Poss": "Yes", "Reflex": "Yes"},
        "erat":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Two", "Number": "Plur", "Poss": "Yes", "Reflex": "Yes"},
        "era":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Two", "Number": "Plur", "Poss": "Yes", "Reflex": "Yes"},
        "deras":        {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Plur", "Poss": "Yes", "Reflex": "Yes"}
    },

    "VBZ": {
        "är":           {"VerbForm": "Fin", "Person": "One", "Tense": "Pres", "Mood": "Ind"},
        "är":           {"VerbForm": "Fin", "Person": "Two", "Tense": "Pres", "Mood": "Ind"},
        "är":           {"VerbForm": "Fin", "Person": "Three", "Tense": "Pres", "Mood": "Ind"},
    },

    "VBP": {
        "är":          {"VerbForm": "Fin", "Tense": "Pres", "Mood": "Ind"}
    },

    "VBD": {
        "var":          {"VerbForm": "Fin", "Tense": "Past", "Number": "Sing"},
        "vart":         {"VerbForm": "Fin", "Tense": "Past", "Number": "Plur"}
    }
}
