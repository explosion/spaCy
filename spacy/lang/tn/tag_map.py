coding: utf8
from __future__ import unicode_literals

from ...symbols import POS, PUNCT, SYM, ADJ, CCONJ, NUM, DET, ADV, ADP, X, VERB
from ...symbols import NOUN, PROPN, PART, INTJ, SPACE, PRON


TAG_MAP = {    
    "INT": {POS: INTJ}, 
    "JUNC": {POS: CCONJ},   
    "$": {POS: PUNCT},   
    "PROPOSS": {POS: PRON},
    "PROQUANT": {POS: PRON},
    "PROEMP": {POS: PRON},
    "NUM": {POS: NUM},
    "N": {POS: NOUN},
    "AUX": {POS: VERB},
    "ADV": {POS: ADV},
    "ADJ": {POS: ADJ},
    "V": {POS: VERB},
    "VCOP": {POS: VERB},
}
