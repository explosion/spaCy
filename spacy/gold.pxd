from cymem.cymem cimport Pool

from .structs cimport TokenC
from .syntax.transition_system cimport Transition

cimport numpy

cdef class GoldParse:
    cdef Pool mem

    cdef int length
    cdef readonly int loss
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

    cdef int* c_tags
    cdef int* c_heads
    cdef int* c_labels
    cdef int** c_brackets
    cdef Transition* c_ner
