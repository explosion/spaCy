# coding: utf8

# structure copied from the English lemmatizer
from __future__ import unicode_literals

from pathlib import Path

from .lookup import LOOKUP
from ._adverbs_wordforms import ADVERBS_WORDFORMS
from ._lemma_rules import ADJECTIVE_RULES, NOUN_RULES, VERB_RULES, PUNCT_RULES
from ....util import load_language_data

ADJECTIVES = set()
ADVERBS = set()
NOUNS = set()
VERBS = set()

LEMMA_INDEX = {"adj": ADJECTIVES, "adv": ADVERBS, "noun": NOUNS, "verb": VERBS}

BASE_PATH = Path(__file__).parent 

LEMMA_EXC = {
    "adj": load_language_data(BASE_PATH / '_adjectives_wordforms.json'),
    "adv": ADVERBS_WORDFORMS,
    "noun": load_language_data(BASE_PATH / '_nouns_wordforms.json'),
    "verb": load_language_data(BASE_PATH / '_verbs_wordforms.json'),
}

LEMMA_RULES = {
    "adj": ADJECTIVE_RULES,
    "noun": NOUN_RULES,
    "verb": VERB_RULES,
    "punct": PUNCT_RULES,
}

# Note on noun wordforms / lemmas:
# All wordforms are extracted from Norsk Ordbank in Norwegian Bokmål 2005, updated 20180627
# (CLARINO NB - Språkbanken), Nasjonalbiblioteket, Norway:
# https://www.nb.no/sprakbanken/show?serial=oai%3Anb.no%3Asbr-5&lang=en
# License:
# Creative_Commons-BY (CC-BY) (https://creativecommons.org/licenses/by/4.0/)


