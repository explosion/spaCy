# coding: utf8
from __future__ import unicode_literals

from ...symbols import LEMMA, PRON_LEMMA

_postpositions = [
        "geçe",
        "gibi",
        "göre",
        "ilişkin",
        "kadar",
        "kala",
        "karşın",
        "nazaran"
        "rağmen",
        "üzere"
        ]

_subordinating_conjunctions = [
        "eğer",
        "madem",
        "mademki",
        "şayet"
        ]

_coordinating_conjunctions = [
        "ama",
        "hem",
        "fakat",
        "ila",
        "lakin",
        "ve",
        "veya",
        "veyahut"
        ]

MORPH_RULES = {
        "ADP": {word: {"POS": "ADP"} for word in _postpositions},
        "SCONJ": {word: {"POS": "SCONJ"} for word in _subordinating_conjunctions},
        "CCONJ": {word: {"POS": "CCONJ"} for word in _coordinating_conjunctions},
        "PRON": {
            }
    }
        
