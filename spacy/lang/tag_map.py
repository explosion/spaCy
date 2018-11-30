# coding: utf8
from __future__ import unicode_literals

from ..symbols import POS, ADV, NOUN, ADP, PRON, SCONJ, PROPN, DET, SYM, INTJ
from ..symbols import PUNCT, NUM, AUX, X, CONJ, ADJ, VERB, PART, SPACE, CCONJ


TAG_MAP = {
    "ADV": {POS: ADV},
    "NOUN": {POS: NOUN},
    "ADP": {POS: ADP},
    "PRON": {POS: PRON},
    "SCONJ": {POS: SCONJ},
    "PROPN": {POS: PROPN},
    "DET": {POS: DET},
    "SYM": {POS: SYM},
    "INTJ": {POS: INTJ},
    "PUNCT": {POS: PUNCT},
    "NUM": {POS: NUM},
    "AUX": {POS: AUX},
    "X": {POS: X},
    "CONJ": {POS: CONJ},
    "CCONJ": {POS: CCONJ},
    "ADJ": {POS: ADJ},
    "VERB": {POS: VERB},
    "PART": {POS: PART},
    "_SP": {POS: SPACE},
}
