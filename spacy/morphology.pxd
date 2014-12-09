from .tokens cimport TokenC, Morphology
from .lexeme cimport Lexeme
from .utf8string cimport StringStore

from preshed.maps cimport PreshMapArray
from cymem.cymem cimport Pool

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


cdef struct PosTag:
    Morphology morph
    int id
    univ_tag_t pos


cdef class Morphologizer:
    cdef Pool mem
    cdef StringStore strings
    cdef object lemmatizer
    cdef PosTag* tags
    cdef readonly list tag_names

    cdef PreshMapArray _cache
    cdef int lemmatize(self, const univ_tag_t pos, const Lexeme* lex) except -1
    cdef int set_morph(self, const int i, TokenC* tokens) except -1
