# coding: utf8
from __future__ import unicode_literals

from ...symbols import POS, PUNCT, SYM, ADJ, NUM, DET, ADV, ADP, X, VERB
from ...symbols import NOUN, PROPN, PART, INTJ, SPACE, PRON, SCONJ, AUX, CONJ, CCONJ

"""
sources:
1. http://www.ldcil.org/Download/Tagset/LDCIL/5Gujrati.pdf
2. http://www.ldcil.org/Corpora/POS/LDCIL_Text_Annotation_BIS_Tagset_Sample_Gujarati.pdf
3. http://vidya.gujaratuniversity.ac.in/data/17.%20POS%20Tagging%20and%20Parsing%20of%20Gujarati%20Language.pdf
"""


TAG_MAP = {
    "N_NN": {POS: NOUN},
    "N_NNP": {POS: PROPN, "NounType": "prop"},
    "N_NST": {POS: PROPN, "NounType": "prop"},
    "PR_PRP": {POS: PRON, "PronType": "prs"},
    "PR_PRF": {POS: PRON, "PronType": "prs", "Reflex": "yes"},
    "PR_PRL": {POS: PRON, "PronType": "rel"},
    "PR_PRC": {POS: PRON, "PronType": "rcp"},
    "PR_PRQ": {POS: PRON, "PronType": "int"},
    "PR_PRI": {POS: PRON, "PronType": "ind"},
    "JJ": {POS: ADJ},
    "RB": {POS: ADV},
    "PSP": {POS: ADP},
    "CC_CCD": {POS: CONJ},
    "CC_CCS": {POS: SCONJ},
    "V_VM": {POS: VERB},
    "V_VM_VF": {POS: VERB, "VerbForm": "fin"},
    "V_VM_VNF": {POS: VERB, "VerbForm": "part"},
    "V_VM_VINF": {POS: VERB, "VerbForm": "inf"},
    "V_VAUX": {POS: AUX},
    "RP_RPD": {POS: PART, "PartType": "emp"},
    "RP_INS": {POS: PART, "PartType": "int"},
    "RP_INTF": {POS: PART},
    "RP_NEG": {POS: PART, "PartType": "neg"},
    "DM_DMD": {POS: DET, "PronType": "dem"},
    "DM_DMR": {POS: DET, "PronType": "rel"},
    "DM_DMQ": {POS: DET, "PronType": "int"},
    "DM_DMI": {POS: DET, "PronType": "ind"},
    "QT_QTF": {POS: DET},
    "QT_QTC": {POS: DET, "NumType": "card"},
    "QT_QTO": {POS: DET, "NumType": "ord"},
    "RD_RDF": {POS: X, "Foreign": "yes"},
    "RD_SYM": {POS: SYM},
    "RD_PUNC": {POS: PUNCT},
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
