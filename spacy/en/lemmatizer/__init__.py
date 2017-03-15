from ._adjectives import ADJECTIVES
from ._adjectives_irreg import ADJECTIVES_IRREG
from ._adverbs import ADVERBS
from ._adverbs_irreg import ADVERBS_IRREG
from ._nouns import NOUNS
from ._nouns_irreg import NOUNS_IRREG
from ._verbs import VERBS
from ._verbs_irreg import VERBS_IRREG
from ._lemma_rules import ADJECTIVE_RULES, NOUN_RULES, VERB_RULES, PUNCT_RULES


INDEX = {
    "adj": ADJECTIVES,
    "adv": ADVERBS,
    "noun": NOUNS,
    "verb": VERBS
}


EXC = {
    "adj": ADJECTIVES_IRREG,
    "adv": ADVERBS_IRREG,
    "noun": NOUNS_IRREG,
    "verb": VERBS_IRREG
}


RULES = {
    "adj": ADJECTIVE_RULES,
    "noun": NOUN_RULES,
    "verb": VERB_RULES,
    "punct": PUNCT_RULES
}
