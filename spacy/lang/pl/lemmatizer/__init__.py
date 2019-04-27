# coding: utf8
from __future__ import unicode_literals

from ._adjectives import ADJECTIVES
from ._adverbs import ADVERBS
from ._nouns import NOUNS
from ._participles import PARTICIPLES
from ._verbs import VERBS
from ._other import OTHER

from ._adjective_rules import ADJECTIVE_RULES
from ._adverb_rules import ADVERB_RULES
from ._noun_rules import NOUN_RULES
from ._participle_rules import PARTICIPLE_RULES
from ._verb_rules import VERB_RULES
# from ._other_rules import OTHER_RULES


LEMMA_INDEX = {'adj': ADJECTIVES, 'adv': ADVERBS, 'noun': NOUNS,
               'part': PARTICIPLES, 'verb': VERBS, 'other': OTHER}

LEMMA_EXC = {}

LEMMA_RULES = {'adj': ADJECTIVE_RULES, 'adv': ADVERB_RULES, 'noun': NOUN_RULES,
               'part': PARTICIPLE_RULES, 'verb': VERB_RULES}
