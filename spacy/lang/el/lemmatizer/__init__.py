# coding: utf8
from __future__ import unicode_literals

from ._adjectives import ADJECTIVES
from ._adjectives_irreg import ADJECTIVES_IRREG
from ._adverbs import ADVERBS
from ._nouns_irreg import NOUNS_IRREG
from ._dets_irreg import DETS_IRREG
from ._verbs_irreg import VERBS_IRREG
from ._nouns import NOUNS
from ._verbs import VERBS
from ._lemma_rules import ADJECTIVE_RULES, NOUN_RULES, VERB_RULES, PUNCT_RULES


LEMMA_INDEX = {"adj": ADJECTIVES, "adv": ADVERBS, "noun": NOUNS, "verb": VERBS}


LEMMA_RULES = {
    "adj": ADJECTIVE_RULES,
    "noun": NOUN_RULES,
    "verb": VERB_RULES,
    "punct": PUNCT_RULES,
}

LEMMA_EXC = {
    "adj": ADJECTIVES_IRREG,
    "noun": NOUNS_IRREG,
    "det": DETS_IRREG,
    "verb": VERBS_IRREG,
}
