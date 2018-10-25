# coding: utf8
from __future__ import unicode_literals

from ..symbols import POS, ADV, NOUN, ADP, PRON, SCONJ, PROPN, DET, SYM, INTJ
from ..symbols import PUNCT, NUM, AUX, X, CONJ, ADJ, VERB, PART, SPACE, CCONJ


# Add a tag map
# Documentation: https://spacy.io/docs/usage/adding-languages#tag-map
# Universal Dependencies: http://universaldependencies.org/u/pos/all.html
# The keys of the tag map should be strings in your tag set. The dictionary must
# have an entry POS whose value is one of the Universal Dependencies tags.
# Optionally, you can also include morphological features or other attributes.


TAG_MAP = {
    "ADV":      {POS: ADV},
    "NOUN":     {POS: NOUN},
    "ADP":      {POS: ADP},
    "PRON":     {POS: PRON},
    "SCONJ":    {POS: SCONJ},
    "PROPN":    {POS: PROPN},
    "DET":      {POS: DET},
    "SYM":      {POS: SYM},
    "INTJ":     {POS: INTJ},
    "PUNCT":    {POS: PUNCT},
    "NUM":      {POS: NUM},
    "AUX":      {POS: AUX},
    "X":        {POS: X},
    "CONJ":     {POS: CONJ},
    "CCONJ":    {POS: CCONJ},
    "ADJ":      {POS: ADJ},
    "VERB":     {POS: VERB},
    "PART":     {POS: PART},
    "SP":     	{POS: SPACE}
}