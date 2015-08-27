from ._ml cimport Model
from .structs cimport TokenC
from .vocab cimport Vocab


cdef class Tagger:
    cdef readonly Vocab vocab
    cdef readonly Model model
    cdef public dict freqs

    cdef int predict(self, int i, const TokenC* tokens) except -1
    cdef int update(self, int i, const TokenC* tokens, int gold) except -1
