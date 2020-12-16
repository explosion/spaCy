# coding: utf8
from __future__ import unicode_literals
from ...symbols import ORTH, LEMMA

_exc = {}

for raw, lemma in [
    ("a-a", "a-o"),
    ("a-e", "a-o"),
    ("a-o", "a-o"),
    ("a-i", "a-o"),
    ("co-a", "co-o"),
    ("co-e", "co-o"),
    ("co-i", "co-o"),
    ("co-o", "co-o"),
    ("da-a", "da-o"),
    ("da-e", "da-o"),
    ("da-i", "da-o"),
    ("da-o", "da-o"),
    ("pe-a", "pe-o"),
    ("pe-e", "pe-o"),
    ("pe-i", "pe-o"),
    ("pe-o", "pe-o"),
]:
    for orth in [raw, raw.capitalize()]:
        _exc[orth] = [{ORTH: orth, LEMMA: lemma}]

# Prefix + prepositions with à (e.g. "sott'a-o")

for prep, prep_lemma in [
    ("a-a", "a-o"),
    ("a-e", "a-o"),
    ("a-o", "a-o"),
    ("a-i", "a-o"),
]:
    for prefix, prefix_lemma in [
        ("sott'", "sotta"),
        ("sott’", "sotta"),
        ("contr'", "contra"),
        ("contr’", "contra"),
        ("ch'", "che"),
        ("ch’", "che"),
        ("s'", "se"),
        ("s’", "se"),
    ]:
        for prefix_orth in [prefix, prefix.capitalize()]:
            _exc[prefix_orth + prep] = [
                {ORTH: prefix_orth, LEMMA: prefix_lemma},
                {ORTH: prep, LEMMA: prep_lemma},
            ]

TOKENIZER_EXCEPTIONS = _exc
