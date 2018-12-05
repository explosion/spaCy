# coding: utf8
from __future__ import unicode_literals

from ._adjectives import ADJECTIVES
from ._nouns import NOUNS
from ._verbs import VERBS
from ._other import OTHER
from ._adjective_rules import ADJECTIVE_RULES
from ._noun_rules import NOUN_RULES
from ._verb_rules import VERB_RULES
from ._other_rules import OTHER_RULES


LEMMA_INDEX = {'adj': ADJECTIVES, 'noun': NOUNS, 'verb': VERBS, 'other': OTHER}

LEMMA_EXC = {}

LEMMA_RULES = {'adj': ADJECTIVE_RULES, 'noun': NOUN_RULES, 'verb': VERB_RULES,
               'other': OTHER_RULES}
