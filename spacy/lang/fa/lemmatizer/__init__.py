# coding: utf8
from __future__ import unicode_literals

from ._adjectives import ADJECTIVES
from ._adjectives_exc import ADJECTIVES_EXC
from ._nouns import NOUNS
from ._nouns_exc import NOUNS_EXC
from ._verbs import VERBS
from ._verbs_exc import VERBS_EXC
from ._lemma_rules import ADJECTIVE_RULES, NOUN_RULES, VERB_RULES, PUNCT_RULES


LEMMA_INDEX = {"adj": ADJECTIVES, "noun": NOUNS, "verb": VERBS}

LEMMA_RULES = {
    "adj": ADJECTIVE_RULES,
    "noun": NOUN_RULES,
    "verb": VERB_RULES,
    "punct": PUNCT_RULES,
}

LEMMA_EXC = {"adj": ADJECTIVES_EXC, "noun": NOUNS_EXC, "verb": VERBS_EXC}
