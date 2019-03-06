# coding: utf8
from __future__ import unicode_literals

from .lookup import LOOKUP
from ._adjectives import ADJECTIVES
from ._adjectives_irreg import ADJECTIVES_IRREG
from ._adp_irreg import ADP_IRREG
from ._adverbs import ADVERBS
from ._auxiliary_verbs_irreg import AUXILIARY_VERBS_IRREG
from ._cconj_irreg import CCONJ_IRREG
from ._dets_irreg import DETS_IRREG
from ._lemma_rules import ADJECTIVE_RULES, NOUN_RULES, VERB_RULES
from ._nouns import NOUNS
from ._nouns_irreg import NOUNS_IRREG
from ._pronouns_irreg import PRONOUNS_IRREG
from ._sconj_irreg import SCONJ_IRREG
from ._verbs import VERBS
from ._verbs_irreg import VERBS_IRREG


LEMMA_INDEX = {'adj': ADJECTIVES, 'adv': ADVERBS, 'noun': NOUNS, 'verb': VERBS}

LEMMA_EXC = {'adj': ADJECTIVES_IRREG, 'adp': ADP_IRREG, 'aux': AUXILIARY_VERBS_IRREG,
             'cconj': CCONJ_IRREG, 'det': DETS_IRREG, 'noun': NOUNS_IRREG, 'verb': VERBS_IRREG, 
             'pron': PRONOUNS_IRREG, 'sconj': SCONJ_IRREG}

LEMMA_RULES = {'adj': ADJECTIVE_RULES, 'noun': NOUN_RULES, 'verb': VERB_RULES}
