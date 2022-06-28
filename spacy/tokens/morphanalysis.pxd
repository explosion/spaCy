from ..vocab cimport Vocab
from ..typedefs cimport hash_t
from ..morphology cimport MorphAnalysisC
from libcpp.memory cimport shared_ptr


cdef class MorphAnalysis:
    cdef readonly Vocab vocab
    cdef readonly hash_t key
    cdef shared_ptr[MorphAnalysisC] c

    cdef void _init_c(self, hash_t key)
