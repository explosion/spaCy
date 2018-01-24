# coding: utf8
"""Based on Garman tag map, converted using
https://pdfs.semanticscholar.org/87b9/24e2134f6782acc59ab567f6bf87cb5e5d9f.pdf"""
from __future__ import unicode_literals

from ...symbols import POS, PUNCT, ADJ, CONJ, CCONJ, SCONJ, SYM, NUM, DET, ADV, ADP, X, VERB
from ...symbols import NOUN, PROPN, PART, INTJ, SPACE, PRON, AUX


TAG_MAP = {
    "$(":       {POS: PUNCT, "PunctType": "PUNCT"},
    "$)":       {POS: PUNCT, "PunctType": "PUNCT"},
        # <parentes-slutt> PUNCT
        # <parentes-beg> PUNCT
    "$,":       {POS: PUNCT, "PunctType": "PUNCT"},
    "$.":       {POS: PUNCT, "PunctType": "PUNCT"},
    "$\"":      {POS: PUNCT, "PunctType": "PUNCT"},
    "$-":       {POS: PUNCT, "PunctType": "PUNCT"},

    'NOUN': {POS: NOUN},
    'PROPN': {POS: PROPN},
    'VERB': {POS: VERB},
    'PUNCT': {POS: PUNCT},
    'ADJ': {POS: ADJ},
    'ADP': {POS: ADP},
    'PART': {POS: PART},
    'DET': {POS: DET},
    'AUX': {POS: AUX},
    'PRON': {POS: PRON},
    'CCONJ': {POS: CCONJ},
    'NUM': {POS: NUM},
    'ADV': {POS: ADV},
    'SCONJ': {POS: SCONJ},
    'SYM': {POS: SYM},
    'X': {POS: X},
    'INTJ': {POS: INTJ},

    # <anf> PUNCT
    # 'adj':      {POS: ADJ},
    # 'adv':      {POS: ADV},
    # 'clb':      {POS: PUNCT}, # SYM
    # 'det':      {POS: DET}, # NUM
    # 'konj':     {POS: CONJ},
    # 'interj':   {POS: INTJ},
    # 'inf-merke': {POS: PART},
    # 'prep':     {POS: ADP},
    # # 'prep':     {POS: ADV},
    # 'pron':     {POS: PRON},
    # 'sbu':      {POS: SCONJ}, #
    # 'subst':    {POS: NOUN}, #, PROPN
    # 'symb':     {POS: SYM}, #
    # 'ukjent':   {POS: X}, #
    # 'verb':     {POS: AUX}, #, VERB

}
