from ._ml cimport Model
from .structs cimport TokenC
from .vocab cimport Vocab


cdef class Tagger:
    cdef readonly Vocab vocab
    cdef readonly Model model
    cdef public dict freqs
