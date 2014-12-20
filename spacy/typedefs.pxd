from libc.stdint cimport uint16_t, uint32_t, uint64_t, uintptr_t
from libc.stdint cimport uint8_t


# Google universal tag set
cpdef enum univ_tag_t:
    NO_TAG
    ADJ
    ADV
    ADP
    CONJ
    DET
    NOUN
    NUM
    PRON
    PRT
    VERB
    X
    PUNCT
    EOL
    N_UNIV_TAGS


ctypedef uint64_t hash_t
ctypedef char* utf8_t
ctypedef uint32_t attr_t
ctypedef uint64_t flags_t
ctypedef uint32_t id_t
ctypedef uint16_t len_t
ctypedef uint16_t tag_t


