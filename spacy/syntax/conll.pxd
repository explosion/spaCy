from cymem.cymem cimport Pool

from ..structs cimport TokenC
from .transition_system cimport Transition

cimport numpy

cdef class GoldParse:
    cdef Pool mem

    cdef int length
    cdef readonly int loss
    cdef readonly list tags
    cdef readonly list heads
    cdef readonly list labels
    cdef readonly list ner

    cdef int* c_tags
    cdef int* c_heads
    cdef int* c_labels
    cdef Transition* c_ner

    cdef int heads_correct(self, TokenC* tokens, bint score_punct=?) except -1
