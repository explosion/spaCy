from ..vocab cimport Vocab
from ..typedefs cimport hash_t
from ..structs cimport MorphAnalysisC


cdef class MorphAnalysis:
    cdef readonly Vocab vocab
    cdef hash_t key
    cdef MorphAnalysisC c
