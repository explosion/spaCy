from cymem.cymem cimport Pool

from .structs cimport TokenC
from .syntax.transition_system cimport Transition


cdef struct GoldParseC:
    int* tags
    int* heads
    int* labels
    int** brackets
    Transition* ner


cdef class GoldParse:
    cdef Pool mem

    cdef GoldParseC c

    cdef int length
    cdef readonly int loss
    cdef readonly list words
    cdef readonly list tags
    cdef readonly list heads
    cdef readonly list labels
    cdef readonly dict orths
    cdef readonly list ner
    cdef readonly list ents
    cdef readonly dict brackets

    cdef readonly list cand_to_gold
    cdef readonly list gold_to_cand
    cdef readonly list orig_annot


