# coding: utf8

from __future__ import unicode_literals

from ...symbols import POS, PUNCT, SYM, ADJ, CCONJ, NUM, DET, ADV, ADP, X, VERB 
from ...symbols import NOUN, PROPN, PART, INTJ, SPACE, PRON, AUX, SCONJ 


# POS explanations for indonesian available from https://www.aclweb.org/anthology/Y12-1014


TAG_MAP = {
    "NSD" : {POS: NOUN}, 
    "Z–" : {POS: PUNCT},
    "VSA" : {POS: VERB}, 
    "CC-" : {POS: NUM}, 
    "R–" : {POS: ADP}, 
    "D–" : {POS: ADV},
    "ASP": {POS: ADJ}, 
    "S–" : {POS: SCONJ}, 
    "VSP" : {POS: VERB}, 
    "H–" : {POS: CCONJ}, 
    "F–" : {POS: X}, 
    "B–" : {POS: DET}, 
    "CO-" : {POS: NUM},
    "G–" : {POS: ADV}, 
    "PS3" : {POS: PRON}, 
    "W–" : {POS: ADV}, 
    "O–" : {POS: AUX}, 
    "PP1" : {POS: PRON}, 
    "ASS" : {POS: ADJ}, 
    "PS1" : {POS: PRON}, 
    "APP" : {POS: ADJ}, 
    "CD-" : {POS: NUM}, 
    "VPA" : {POS: VERB}, 
    "VPP" : {POS: VERB},
}
