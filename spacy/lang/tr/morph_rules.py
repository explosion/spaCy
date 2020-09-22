# coding: utf8
from __future__ import unicode_literals

from ...symbols import LEMMA, PRON_LEMMA

_subordinating_conjunctions = [
        "eğer",
        "madem",
        "mademki",
        "şayet",
        ]

_coordinating_conjunctions = [
        "ama",
        "hem"
        "fakat",
        "ve",
        "veya"
        ]

MORPH_RULES = {
        "SCONJ": {word: {"POS": "SCONJ"} for word in _subordinating_conjunctions},
        "CCONJ": {word: {"POS": "CCONJ"} for word in _coordinating_conjunctions},
        "PRON": {
            }
    }
        
