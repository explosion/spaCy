from . cimport symbols


cpdef enum univ_pos_t:
    NO_TAG = 0
    ADJ = symbols.ADJ
    ADP = symbols.ADP
    ADV = symbols.ADV
    AUX = symbols.AUX
    CONJ = symbols.CONJ
    CCONJ = symbols.CCONJ  # U20
    DET = symbols.DET
    INTJ = symbols.INTJ
    NOUN = symbols.NOUN
    NUM = symbols.NUM
    PART = symbols.PART
    PRON = symbols.PRON
    PROPN = symbols.PROPN
    PUNCT = symbols.PUNCT
    SCONJ = symbols.SCONJ
    SYM = symbols.SYM
    VERB = symbols.VERB
    X = symbols.X
    EOL = symbols.EOL
    SPACE = symbols.SPACE
