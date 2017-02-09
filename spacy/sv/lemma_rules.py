# encoding: utf8
from __future__ import unicode_literals


LEMMA_RULES = {
    "noun": [
        ["t", ""],
        ["n", ""],
        ["na", ""],
        ["na", "e"],
        ["or", "a"],
        ["orna", "a"],
        ["et", ""],
        ["en", ""],
        ["en", "e"],
        ["er", ""],
        ["erna", ""],
        ["ar", "e"],
        ["ar", ""],
        ["lar", "el"],
        ["arna", "e"],
        ["arna", ""],
        ["larna", "el"]
    ],

    "adj": [
        ["are", ""],
        ["ast", ""],
        ["re", ""],
        ["st", ""],
        ["ägre", "åg"],
        ["ägst", "åg"],
        ["ängre", "ång"],
        ["ängst", "ång"],
        ["örre", "or"],
        ["örst", "or"],
    ],

    "punct": [
        ["“", "\""],
        ["”", "\""],
        ["\u2018", "'"],
        ["\u2019", "'"]
    ]
}
