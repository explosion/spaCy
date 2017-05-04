from thinc.typedefs cimport atom_t

from .stateclass cimport StateClass
from .arc_eager cimport TransitionSystem
from ..vocab cimport Vocab
from ..tokens.doc cimport Doc
from ..structs cimport TokenC
from ._state cimport StateC


cdef class Parser:
    cdef readonly Vocab vocab
    cdef readonly object model
    cdef readonly TransitionSystem moves
    cdef readonly object cfg

    #cdef int parseC(self, TokenC* tokens, int length, int nr_feat) nogil
