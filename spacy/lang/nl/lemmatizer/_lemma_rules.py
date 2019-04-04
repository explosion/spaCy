# coding: utf8
from __future__ import unicode_literals


ADJECTIVE_SUFFIX_RULES = [
    ["sten", ""],
    ["ste", ""],
    ["st", ""],
    ["er", ""],
    ["en", ""],
    ["e", ""],
    ["ende", "end"]
]

VERB_SUFFIX_RULES = [
    ["dt", "den"],
    ["de", "en"],
    ["te", "en"],
    ["dde", "den"],
    ["tte", "ten"],
    ["dden", "den"],
    ["tten", "ten"],
    ["end", "en"],
]

NOUN_SUFFIX_RULES = [
    ["en", ""],
    ["ën", ""],
    ["'er", ""],
    ["s", ""],
    ["tje", ""],
    ["kje", ""],
    ["'s", ""],
    ["ici", "icus"],
    ["heden", "heid"],
    ["elen", "eel"],
    ["ezen", "ees"],
    ["even", "eef"],
    ["ssen", "s"],
    ["rren", "r"],
    ["kken", "k"],
    ["bben", "b"]
]

NUM_SUFFIX_RULES = [
    ["ste", ""],
    ["sten", ""],
    ["ën", ""],
    ["en", ""],
    ["de", ""],
    ["er", ""],
    ["ër", ""],
    ["tjes", ""]
]

PUNCT_SUFFIX_RULES = [
    ["“", "\""],
    ["”", "\""],
    ["\u2018", "'"],
    ["\u2019", "'"]
]


# In-place sort guaranteeing that longer -- more specific -- rules are
# applied first.
for rule_set in (ADJECTIVE_SUFFIX_RULES,
                 NOUN_SUFFIX_RULES,
                 NUM_SUFFIX_RULES,
                 VERB_SUFFIX_RULES):
    rule_set.sort(key=lambda r: len(r[0]), reverse=True)


RULES = {
    "adj": ADJECTIVE_SUFFIX_RULES,
    "noun": NOUN_SUFFIX_RULES,
    "verb": VERB_SUFFIX_RULES,
    "num": NUM_SUFFIX_RULES,
    "punct": PUNCT_SUFFIX_RULES
}
