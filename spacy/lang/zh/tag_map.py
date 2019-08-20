# coding: utf8
from __future__ import unicode_literals

from ...symbols import POS, PUNCT, ADJ, CONJ, CCONJ, NUM, DET, ADV, ADP, X, VERB
from ...symbols import NOUN, PART, INTJ, PRON

# The Chinese part-of-speech tagger uses the OntoNotes 5 version of the Penn Treebank tag set.
# We also map the tags to the simpler Google Universal POS tag set.

TAG_MAP = {
    "AS": {POS: PART},
    "DEC": {POS: PART},
    "DEG": {POS: PART},
    "DER": {POS: PART},
    "DEV": {POS: PART},
    "ETC": {POS: PART},
    "LC": {POS: PART},
    "MSP": {POS: PART},
    "SP": {POS: PART},
    "BA": {POS: X},
    "FW": {POS: X},
    "IJ": {POS: INTJ},
    "LB": {POS: X},
    "ON": {POS: X},
    "SB": {POS: X},
    "X": {POS: X},
    "URL": {POS: X},
    "INF": {POS: X},
    "NN": {POS: NOUN},
    "NR": {POS: NOUN},
    "NT": {POS: NOUN},
    "VA": {POS: VERB},
    "VC": {POS: VERB},
    "VE": {POS: VERB},
    "VV": {POS: VERB},
    "CD": {POS: NUM},
    "M": {POS: NUM},
    "OD": {POS: NUM},
    "DT": {POS: DET},
    "CC": {POS: CCONJ},
    "CS": {POS: CONJ},
    "AD": {POS: ADV},
    "JJ": {POS: ADJ},
    "P": {POS: ADP},
    "PN": {POS: PRON},
    "PU": {POS: PUNCT},
}
