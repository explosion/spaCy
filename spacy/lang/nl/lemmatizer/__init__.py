# coding: utf8
from __future__ import unicode_literals

from pathlib import Path

from ._verbs_irreg import VERBS_IRREG
from ._nouns_irreg import NOUNS_IRREG
from ._adjectives_irreg import ADJECTIVES_IRREG
from ._adverbs_irreg import ADVERBS_IRREG

from ._adpositions_irreg import ADPOSITIONS_IRREG
from ._determiners_irreg import DETERMINERS_IRREG
from ._pronouns_irreg import PRONOUNS_IRREG

from ._verbs import VERBS
from ._adjectives import ADJECTIVES

from ._adpositions import ADPOSITIONS
from ._determiners import DETERMINERS

from ._lemma_rules import RULES
from .lemmatizer import DutchLemmatizer

from ....util import load_language_data

BASE_PATH = Path(__file__).parent

LOOKUP = load_language_data(BASE_PATH / "lookup.json")
NOUNS = load_language_data(BASE_PATH / "_nouns.json")

LEMMA_INDEX = {
    "adj": ADJECTIVES,
    "noun": NOUNS,
    "verb": VERBS,
    "adp": ADPOSITIONS,
    "det": DETERMINERS,
}

LEMMA_EXC = {
    "adj": ADJECTIVES_IRREG,
    "adv": ADVERBS_IRREG,
    "adp": ADPOSITIONS_IRREG,
    "noun": NOUNS_IRREG,
    "verb": VERBS_IRREG,
    "det": DETERMINERS_IRREG,
    "pron": PRONOUNS_IRREG,
}

__all__ = ["LOOKUP", "LEMMA_EXC", "LEMMA_INDEX", "RULES", "DutchLemmatizer"]
