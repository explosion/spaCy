from cymem.cymem cimport Pool

from ..structs cimport TokenC
from .transition_system cimport Transition


cdef class GoldParse:
    cdef Pool mem

    cdef int length
    cdef readonly int loss
    cdef readonly object ids
    cdef readonly object tags
    cdef readonly object heads
    cdef readonly object labels

    cdef readonly object tags_
    cdef readonly object labels_
    cdef readonly object ner_

    cdef Transition* ner
    cdef int* c_heads
    cdef int* c_labels

    cdef int heads_correct(self, TokenC* tokens, bint score_punct=?) except -1


cdef class NERAnnotation:
    cdef Pool mem
    cdef int* starts
    cdef int* ends
    cdef int* labels
    cdef readonly list entities
