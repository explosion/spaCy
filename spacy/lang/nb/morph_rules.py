# encoding: utf8
from __future__ import unicode_literals

from ...symbols import LEMMA, PRON_LEMMA


# Used the table of pronouns at https://no.wiktionary.org/wiki/Tillegg:Pronomen_i_norsk

MORPH_RULES = {
    "PRP": {
        "jeg":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Sing", "Case": "Nom"},
        "meg":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Sing", "Case": "Acc"},
        "du":           {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Two", "Number": "Sing", "Case": "Nom"},
        "deg":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Two", "Number": "Sing", "Case": "Acc"},
        "han":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Gender": "Masc", "Case": "Nom"},
        "ham":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Gender": "Masc", "Case": "Acc"},
        "han":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Gender": "Masc", "Case": "Acc"},
        "hun":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Gender": "Fem",  "Case": "Nom"},
        "henne":        {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Gender": "Fem",  "Case": "Acc"},
        "den":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Gender": "Neut"},
        "det":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Gender": "Neut"},
        "seg":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Reflex": "Yes"},
        "vi":           {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Plur", "Case": "Nom"},
        "oss":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Plur", "Case": "Acc"},
        "dere":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Two", "Number": "Plur", "Case": "Nom"},
        "de":           {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Plur", "Case": "Nom"},
        "dem":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Plur", "Case": "Acc"},
        "seg":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Plur", "Reflex": "Yes"},

        "min":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Sing", "Poss": "Yes", "Gender": "Masc"},
        "mi":           {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Sing", "Poss": "Yes", "Gender": "Fem"},
        "mitt":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Sing", "Poss": "Yes", "Gender": "Neu"},
        "mine":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Plur", "Poss": "Yes"},
        "din":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Two", "Number": "Sing", "Poss": "Yes", "Gender": "Masc"},
        "di":           {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Two", "Number": "Sing", "Poss": "Yes", "Gender": "Fem"},
        "ditt":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Two", "Number": "Sing", "Poss": "Yes", "Gender": "Neu"},
        "dine":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Two", "Number": "Plur", "Poss": "Yes"},
        "hans":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Poss": "Yes", "Gender": "Masc"},
        "hennes":       {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Poss": "Yes", "Gender": "Fem"},
        "dens":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Poss": "Yes", "Gender": "Neu"},
        "dets":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Poss": "Yes", "Gender": "Neu"},
        "vår":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Plur", "Poss": "Yes"},
        "vårt":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Plur", "Poss": "Yes"},
        "våre":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Plur", "Poss": "Yes", "Gender":"Neu"},
        "deres":        {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Plur", "Poss": "Yes", "Gender":"Neu", "Reflex":"Yes"},
        "sin":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Sing", "Poss": "Yes", "Gender":"Masc", "Reflex":"Yes"},
        "si":           {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Sing", "Poss": "Yes", "Gender":"Fem", "Reflex":"Yes"},
        "sitt":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Sing", "Poss": "Yes", "Gender":"Neu", "Reflex":"Yes"},
        "sine":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Plur", "Poss": "Yes", "Reflex":"Yes"},
    },

    "VBZ": {
        "er":           {"VerbForm": "Fin", "Person": "One", "Tense": "Pres", "Mood": "Ind"},
        "er":           {"VerbForm": "Fin", "Person": "Two", "Tense": "Pres", "Mood": "Ind"},
        "er":           {"VerbForm": "Fin", "Person": "Three", "Tense": "Pres", "Mood": "Ind"},
    },

    "VBP": {
        "er":          {"VerbForm": "Fin", "Tense": "Pres", "Mood": "Ind"}
    },

    "VBD": {
        "var":          {"VerbForm": "Fin", "Tense": "Past", "Number": "Sing"},
        "vært":         {"VerbForm": "Fin", "Tense": "Past", "Number": "Plur"}
    }
}
