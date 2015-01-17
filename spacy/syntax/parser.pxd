from .._ml cimport Model

from .arc_eager cimport TransitionSystem

from ..tokens cimport Tokens, TokenC


cdef class GreedyParser:
    cdef object cfg
    cdef readonly Model model
    cdef TransitionSystem moves
