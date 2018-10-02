# coding: utf8
from __future__ import unicode_literals

from .lookup import LOOKUP
from ._adjectives import ADJECTIVES
from ._adjectives_irreg import ADJECTIVES_IRREG
from ._adverbs import ADVERBS
from ._nouns import NOUNS
from ._nouns_irreg import NOUNS_IRREG
from ._verbs import VERBS
from ._verbs_irreg import VERBS_IRREG
from ._dets_irreg import DETS_IRREG
from ._pronouns_irreg import PRONOUNS_IRREG
from ._auxiliary_verbs_irreg import AUXILIARY_VERBS_IRREG
from ._lemma_rules import ADJECTIVE_RULES, NOUN_RULES, VERB_RULES


LEMMA_INDEX = {'adj': ADJECTIVES, 'adv': ADVERBS, 'noun': NOUNS, 'verb': VERBS}

LEMMA_EXC = {'adj': ADJECTIVES_IRREG, 'noun': NOUNS_IRREG, 'verb': VERBS_IRREG, 
             'det': DETS_IRREG, 'pron': PRONOUNS_IRREG, 'aux': AUXILIARY_VERBS_IRREG}

LEMMA_RULES = {'adj': ADJECTIVE_RULES, 'noun': NOUN_RULES, 'verb': VERB_RULES}
