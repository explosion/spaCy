# coding: utf8
from __future__ import unicode_literals

from ...symbols import POS, PUNCT, ADJ, CONJ, NUM, DET, ADV, ADP, X, VERB
from ...symbols import PRON, NOUN, PART, INTJ, AUX


TAG_MAP = {
    "ADJ": {POS: ADJ},
    "ADJ_CMPR": {POS: ADJ},
    "ADJ_INO": {POS: ADJ},
    "ADJ_SUP": {POS: ADJ},
    "ADV": {POS: ADV},
    "ADV_COMP": {POS: ADV},
    "ADV_I": {POS: ADV},
    "ADV_LOC": {POS: ADV},
    "ADV_NEG": {POS: ADV},
    "ADV_TIME": {POS: ADV},
    "CLITIC": {POS: PART},
    "CON": {POS: CONJ},
    "CONJ": {POS: CONJ},
    "DELM": {POS: PUNCT},
    "DET": {POS: DET},
    "FW": {POS: X},
    "INT": {POS: INTJ},
    "N_PL": {POS: NOUN},
    "N_SING": {POS: NOUN},
    "N_VOC": {POS: NOUN},
    "NUM": {POS: NUM},
    "P": {POS: ADP},
    "PREV": {POS: ADP},
    "PRO": {POS: PRON},
    "V_AUX": {POS: AUX},
    "V_IMP": {POS: VERB},
    "V_PA": {POS: VERB},
    "V_PP": {POS: VERB},
    "V_PRS": {POS: VERB},
    "V_SUB": {POS: VERB},
}
