from .parser cimport Parser
from ..structs cimport TokenC
from thinc.typedefs cimport weight_t


cdef class BeamParser(Parser):
    cdef public int beam_width
    cdef public weight_t beam_density

    cdef int _parseC(self, TokenC* tokens, int length, int nr_feat, int nr_class) except -1
