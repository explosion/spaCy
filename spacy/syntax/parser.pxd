from thinc.search cimport Beam

from .._ml cimport Model

from .arc_eager cimport TransitionSystem

from ..tokens cimport Tokens, TokenC


cdef class Parser:
    cdef public object cfg
    cdef public Model model
    cdef public TransitionSystem moves
