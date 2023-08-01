from ..structs cimport MorphAnalysisC
from ..typedefs cimport hash_t
from ..vocab cimport Vocab


cdef class MorphAnalysis:
    cdef readonly Vocab vocab
    cdef readonly hash_t key
    cdef MorphAnalysisC c
