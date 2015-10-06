from .symbols cimport *


cpdef enum univ_pos_t:
    NO_TAG = EMPTY_VALUE
    ADJ = POS_adj
    ADP = POS_adp
    ADV = POS_adv
    AUX = POS_aux
    CONJ = POS_conj
    DET = POS_det
    INTJ = POS_intj
    NOUN = POS_noun
    NUM = POS_num
    PART = POS_part
    PRON = POS_pron
    PROPN = POS_propn
    PUNCT = POS_punct
    SCONJ = POS_sconj
    SYM = POS_sym
    VERB = POS_verb
    X = POS_x
    EOL = POS_eol
    SPACE = POS_space
