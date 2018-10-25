from __future__ import unicode_literals

from ...symbols import POS, ADV, NOUN, ADP, PRON, SCONJ, PROPN, DET, SYM, INTJ
from ...symbols import PUNCT, NUM, AUX, X, ADJ, VERB, PART, SPACE, CCONJ


TAG_MAP = {
    "ADJ": {POS: ADJ},
    "ADV": {POS: ADV},
    "INTJ": {POS: INTJ},
    "NOUN": {POS: NOUN},
    "PROPN": {POS: PROPN},
    "VERB": {POS: VERB},
    "ADP": {POS: ADP},
    "CCONJ": {POS: CCONJ},
    "SCONJ": {POS: SCONJ},
    "PART": {POS: PART},
    "PUNCT": {POS: PUNCT},
    "SYM": {POS: SYM},
    "NUM": {POS: NUM},
    "PRON": {POS: PRON},
    "AUX": {POS: AUX},
    "SPACE": {POS: SPACE},
    "DET": {POS: DET},
    "X": {POS: X}
}
