# encoding: utf8
from __future__ import unicode_literals


LEMMA_RULES = {
    "noun": [
        ["s", ""],
        ["ses", "s"],
        ["ves", "f"],
        ["xes", "x"],
        ["zes", "z"],
        ["ches", "ch"],
        ["shes", "sh"],
        ["men", "man"],
        ["ies", "y"]
    ],

    "verb": [
        ["s", ""],
        ["ies", "y"],
        ["es", "e"],
        ["es", ""],
        ["ed", "e"],
        ["ed", ""],
        ["ing", "e"],
        ["ing", ""]
    ],

    "adj": [
        ["er", ""],
        ["est", ""],
        ["er", "e"],
        ["est", "e"]
    ],

    "punct": [
        ["“", "\""],
        ["”", "\""],
        ["\u2018", "'"],
        ["\u2019", "'"]
    ]
}
