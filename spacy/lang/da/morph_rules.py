# coding: utf8
from __future__ import unicode_literals

from ...symbols import LEMMA, PRON_LEMMA

# Source: Danish Universal Dependencies and http://fjern-uv.dk/pronom.php

# Note: The Danish Universal Dependencies specify Case=Acc for all instances
# of "den"/"det" even when the case is in fact "Nom". In the rules below, Case
# is left unspecified for "den" and "det".

MORPH_RULES = {
    "PRON": {
        "jeg":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Sing", "Case": "Nom", "Gender": "Com"},                      # Case=Nom|Gender=Com|Number=Sing|Person=1|PronType=Prs
        "mig":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Sing", "Case": "Acc", "Gender": "Com"},                      # Case=Acc|Gender=Com|Number=Sing|Person=1|PronType=Prs
        "min":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Sing", "Poss": "Yes", "Gender": "Com"},                      # Gender=Com|Number=Sing|Number[psor]=Sing|Person=1|Poss=Yes|PronType=Prs
        "mit":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Sing", "Poss": "Yes", "Gender": "Neut"},                     # Gender=Neut|Number=Sing|Number[psor]=Sing|Person=1|Poss=Yes|PronType=Prs
        "vor":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Sing", "Poss": "Yes", "Gender": "Com"},                      # Gender=Com|Number=Sing|Number[psor]=Plur|Person=1|Poss=Yes|PronType=Prs|Style=Form
        "vort":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Sing", "Poss": "Yes", "Gender": "Neut"},                     # Gender=Neut|Number=Sing|Number[psor]=Plur|Person=1|Poss=Yes|PronType=Prs|Style=Form
        "du":           {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Two", "Number": "Sing", "Case": "Nom", "Gender": "Com"},                      # Case=Nom|Gender=Com|Number=Sing|Person=2|PronType=Prs
        "dig":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Two", "Number": "Sing", "Case": "Acc", "Gender": "Com"},                      # Case=Acc|Gender=Com|Number=Sing|Person=2|PronType=Prs
        "din":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Two", "Number": "Sing", "Poss": "Yes", "Gender": "Com"},                      # Gender=Com|Number=Sing|Number[psor]=Sing|Person=2|Poss=Yes|PronType=Prs
        "dit":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Two", "Number": "Sing", "Poss": "Yes", "Gender": "Neut"},                     # Gender=Neut|Number=Sing|Number[psor]=Sing|Person=2|Poss=Yes|PronType=Prs
        "han":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Case": "Nom", "Gender": "Com"},                    # Case=Nom|Gender=Com|Number=Sing|Person=3|PronType=Prs
        "hun":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Case": "Nom", "Gender": "Com"},                    # Case=Nom|Gender=Com|Number=Sing|Person=3|PronType=Prs
        "den":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Gender": "Com"},                                   # Case=Acc|Gender=Com|Number=Sing|Person=3|PronType=Prs, See note above.
        "det":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Gender": "Neut"},                                  # Case=Acc|Gender=Neut|Number=Sing|Person=3|PronType=Prs See note above.
        "ham":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Case": "Acc", "Gender": "Com"},                    # Case=Acc|Gender=Com|Number=Sing|Person=3|PronType=Prs
        "hende":        {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Case": "Acc", "Gender": "Com"},                    # Case=Acc|Gender=Com|Number=Sing|Person=3|PronType=Prs
        "sin":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Poss": "Yes", "Gender": "Com", "Reflex": "Yes"},   # Gender=Com|Number=Sing|Number[psor]=Sing|Person=3|Poss=Yes|PronType=Prs|Reflex=Yes
        "sit":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Sing", "Poss": "Yes", "Gender": "Neut", "Reflex": "Yes"},  # Gender=Neut|Number=Sing|Number[psor]=Sing|Person=3|Poss=Yes|PronType=Prs|Reflex=Yes

        "vi":           {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Plur", "Case": "Nom", "Gender": "Com"},                      # Case=Nom|Gender=Com|Number=Plur|Person=1|PronType=Prs
        "os":           {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Plur", "Case": "Acc", "Gender": "Com"},                      # Case=Acc|Gender=Com|Number=Plur|Person=1|PronType=Prs
        "mine":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Plur", "Poss": "Yes"},                                       # Number=Plur|Number[psor]=Sing|Person=1|Poss=Yes|PronType=Prs
        "vore":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Number": "Plur", "Poss": "Yes"},                                       # Number=Plur|Number[psor]=Plur|Person=1|Poss=Yes|PronType=Prs|Style=Form
        "I":            {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Two", "Number": "Plur", "Case": "Nom", "Gender": "Com"},                      # Case=Nom|Gender=Com|Number=Plur|Person=2|PronType=Prs
        "jer":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Two", "Number": "Plur", "Case": "Acc", "Gender": "Com"},                      # Case=Acc|Gender=Com|Number=Plur|Person=2|PronType=Prs
        "dine":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Two", "Number": "Plur", "Poss": "Yes"},                                       # Number=Plur|Number[psor]=Sing|Person=2|Poss=Yes|PronType=Prs
        "de":           {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Plur", "Case": "Nom"},                                     # Case=Nom|Number=Plur|Person=3|PronType=Prs
        "dem":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Plur", "Case": "Acc"},                                     # Case=Acc|Number=Plur|Person=3|PronType=Prs
        "sine":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Number": "Plur", "Poss": "Yes", "Reflex": "Yes"},                    # Number=Plur|Number[psor]=Sing|Person=3|Poss=Yes|PronType=Prs|Reflex=Yes

        "vores":        {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "One", "Poss": "Yes"},                                                         # Number[psor]=Plur|Person=1|Poss=Yes|PronType=Prs
        "De":           {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Two", "Case": "Nom", "Gender": "Com"},                                        # Case=Nom|Gender=Com|Person=2|Polite=Form|PronType=Prs
        "Dem":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Two", "Case": "Acc", "Gender": "Com"},                                        # Case=Acc|Gender=Com|Person=2|Polite=Form|PronType=Prs
        "Deres":        {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Two", "Poss": "Yes"},                                                         # Person=2|Polite=Form|Poss=Yes|PronType=Prs
        "jeres":        {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Two", "Poss": "Yes"},                                                         # Number[psor]=Plur|Person=2|Poss=Yes|PronType=Prs
        "sig":          {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Case": "Acc", "Reflex": "Yes"},                                      # Case=Acc|Person=3|PronType=Prs|Reflex=Yes
        "hans":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Poss": "Yes"},                                                       # Number[psor]=Sing|Person=3|Poss=Yes|PronType=Prs
        "hendes":       {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Poss": "Yes"},                                                       # Number[psor]=Sing|Person=3|Poss=Yes|PronType=Prs
        "dens":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Poss": "Yes"},                                                       # Number[psor]=Sing|Person=3|Poss=Yes|PronType=Prs
        "dets":         {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Poss": "Yes"},                                                       # Number[psor]=Sing|Person=3|Poss=Yes|PronType=Prs
        "deres":        {LEMMA: PRON_LEMMA, "PronType": "Prs", "Person": "Three", "Poss": "Yes"},                                                       # Number[psor]=Plur|Person=3|Poss=Yes|PronType=Prs
    },

    "VERB": {
        "er":           {LEMMA: "være", "VerbForm": "Fin", "Tense": "Pres"},
        "var":          {LEMMA: "være", "VerbForm": "Fin", "Tense": "Past"}
    }
}

for tag, rules in MORPH_RULES.items():
    for key, attrs in dict(rules).items():
        rules[key.title()] = attrs
