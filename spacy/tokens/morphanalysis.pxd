from ..vocab cimport Vocab
from ..typedefs cimport hash_t
from ..morphology cimport MorphAnalysisC


cdef class MorphAnalysis:
    cdef readonly Vocab vocab
    cdef readonly hash_t key
    cdef const MorphAnalysisC* c

    cdef void _init_c(self, hash_t key)
