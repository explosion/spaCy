# coding: utf8
from __future__ import unicode_literals

from ...symbols import POS, PUNCT, ADJ, CONJ, NUM, DET, ADV, ADP, X, VERB
from ...symbols import NOUN, PART, SPACE, AUX

# TODO: tag map is still using POS tags from an internal training set.
# These POS tags have to be modified to match those from Universal Dependencies

TAG_MAP = {
    "$": {POS: PUNCT},
    "ADJ": {POS: ADJ},
    "AV": {POS: ADV},
    "APPR": {POS: ADP, "AdpType": "prep"},
    "APPRART": {POS: ADP, "AdpType": "prep", "PronType": "art"},
    "D": {POS: DET, "PronType": "art"},
    "KO": {POS: CONJ},
    "N": {POS: NOUN},
    "P": {POS: ADV},
    "TRUNC": {POS: X, "Hyph": "yes"},
    "AUX": {POS: AUX},
    "V": {POS: VERB},
    "MV": {POS: VERB, "VerbType": "mod"},
    "PTK": {POS: PART},
    "INTER": {POS: PART},
    "NUM": {POS: NUM},
    "_SP": {POS: SPACE},
}
