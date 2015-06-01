from thinc.search cimport Beam

from .._ml cimport Model

from .arc_eager cimport TransitionSystem

from ..tokens cimport Tokens, TokenC
from ._state cimport State



cdef class Parser:
    cdef readonly object cfg
    cdef readonly Model model
    cdef readonly TransitionSystem moves


    cdef State* _greedy_parse(self, Tokens tokens) except NULL
    cdef State* _beam_parse(self, Tokens tokens) except NULL
