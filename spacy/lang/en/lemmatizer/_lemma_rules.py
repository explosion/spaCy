# coding: utf8
from __future__ import unicode_literals


ADJECTIVE_RULES = [["er", ""], ["est", ""], ["er", "e"], ["est", "e"]]


NOUN_RULES = [
    ["s", ""],
    ["ses", "s"],
    ["ves", "f"],
    ["xes", "x"],
    ["zes", "z"],
    ["ches", "ch"],
    ["shes", "sh"],
    ["men", "man"],
    ["ies", "y"],
]


VERB_RULES = [
    ["s", ""],
    ["ies", "y"],
    ["es", "e"],
    ["es", ""],
    ["ed", "e"],
    ["ed", ""],
    ["ing", "e"],
    ["ing", ""],
]


PUNCT_RULES = [["“", '"'], ["”", '"'], ["\u2018", "'"], ["\u2019", "'"]]
