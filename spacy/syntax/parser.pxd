from .._ml cimport Model

from .arc_eager cimport TransitionSystem

from ..tokens cimport Tokens, TokenC


cdef class GreedyParser:
    cdef readonly object cfg
    cdef readonly Model model
    cdef readonly TransitionSystem moves
