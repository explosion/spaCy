from thinc.search cimport Beam

from .._ml cimport Model

from .arc_eager cimport TransitionSystem

from ..tokens cimport Tokens, TokenC


cdef class Parser:
    cdef readonly object cfg
    cdef readonly Model model
    cdef readonly TransitionSystem moves

    cdef int _greedy_parse(self, Tokens tokens) except -1
    cdef int _beam_parse(self, Tokens tokens) except -1
