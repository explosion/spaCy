# coding: utf8

# structure copied from the English lemmatizer
from __future__ import unicode_literals

from .lookup import LOOKUP
from ._adjectives_wordforms import ADJECTIVES_WORDFORMS
from ._adverbs_wordforms import ADVERBS_WORDFORMS
from ._nouns_wordforms import NOUNS_WORDFORMS
from ._verbs_wordforms import VERBS_WORDFORMS
from ._lemma_rules import ADJECTIVE_RULES, NOUN_RULES, VERB_RULES, PUNCT_RULES
from ._verbs import VERBS
from ._nouns import NOUNS
from ._adjectives import ADJECTIVES
from ._adverbs import ADVERBS

LEMMA_INDEX = {"adj": ADJECTIVES, "adv": ADVERBS, "noun": NOUNS, "verb": VERBS}

LEMMA_EXC = {
    "adj": ADJECTIVES_WORDFORMS,
    "adv": ADVERBS_WORDFORMS,
    "noun": NOUNS_WORDFORMS,
    "verb": VERBS_WORDFORMS,
}

LEMMA_RULES = {
    "adj": ADJECTIVE_RULES,
    "noun": NOUN_RULES,
    "verb": VERB_RULES,
    "punct": PUNCT_RULES,
}
