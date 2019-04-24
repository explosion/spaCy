# coding: utf8
from __future__ import unicode_literals
from ...symbols import POS, PUNCT, SYM, ADJ, CCONJ, SCONJ, NUM, DET, ADV, ADP, X, VERB
from ...symbols import NOUN, PROPN, PART, INTJ, PRON, AUX


TAG_MAP_AUX = {
    "ADJ": {POS: ADJ},
    "ADJA": {POS: ADJ},
    "ADJC": {POS: ADJ},
    "ADJP": {POS: ADJ},
    "ADV": {POS: ADV},
    "AGLT": {POS: VERB},
    "BEDZIE": {POS: VERB},
    "BREV": {POS: X},
    "BURK": {POS: ADV},
    "COMP": {POS: SCONJ},
    "CONJ": {POS: CCONJ},
    "DEPR": {POS: NOUN},
    "FIN": {POS: VERB},
    "GER": {POS: NOUN},
    "IMPS": {POS: VERB},
    "IMPT": {POS: VERB},
    "INF": {POS: VERB},
    "INTERJ": {POS: INTJ},
    "INTERP": {POS: PUNCT},
    "NUM": {POS: NUM},
    "NUMCOL": {POS: NUM},
    "PACT": {POS: VERB},
    "PANT": {POS: VERB},
    "PCON": {POS: VERB},
    "PPAS": {POS: VERB},
    "PPRON12": {POS: PRON},
    "PPRON3": {POS: PRON},
    "PRAET": {POS: VERB},
    "PRED": {POS: VERB},
    "PREP": {POS: ADP},
    "QUB": {POS: PART},
    "SIEBIE": {POS: PRON},
    "SUBST": {POS: NOUN},
    "WINIEN": {POS: VERB},
    "XXX": {POS: X},
}