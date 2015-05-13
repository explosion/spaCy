from .tokens cimport Tokens
from .typedefs cimport flags_t, attr_id_t, attr_t
from .parts_of_speech cimport univ_pos_t
from .structs cimport Morphology, TokenC, LexemeC
from .vocab cimport Vocab
from .strings cimport StringStore


cdef class Span:
    cdef readonly Tokens _seq
    cdef public int i
    cdef public int start
    cdef public int end
    cdef readonly int label
