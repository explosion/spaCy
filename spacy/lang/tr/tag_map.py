# coding: utf8
from __future__ import unicode_literals

from ...symbols import POS, PUNCT, ADJ, CCONJ, SCONJ, NUM, DET, ADV, ADP, X
from ...symbols import NOUN, PROPN, PART, INTJ, SPACE, PRON, AUX, VERB

# UD TR-GB tags

TAG_MAP = {
        "ADJ": {POS: ADJ},
        "ADP": {POS: ADP},
        "ADV": {POS: ADV},
        "AUX": {POS: AUX},
        "CCONJ": {POS: CCONJ},
        "DET": {POS: DET},
        "INTJ": {POS: INTJ},
        "NOUN": {POS: NOUN},
        "NUM": {POS: NUM},
        "PRON": {POS: PRON},
        "PROPN": {POS: PROPN},
        "PUNCT": {POS: PUNCT},
        "SCONJ": {POS: SCONJ},
        "VERB": {POS: VERB},
        "X": {POS: X}
        }
