from libc.stdint cimport uint32_t, uint64_t
from thinc.features cimport Extractor
from thinc.learner cimport LinearModel

from .arc_eager cimport TransitionSystem

from ..tokens cimport Tokens, TokenC
from ._state cimport State
from ..index cimport DecisionMemory


cdef class GreedyParser:
    cdef object cfg
    cdef Extractor extractor
    cdef readonly LinearModel model
    cdef TransitionSystem moves
    cdef readonly DecisionMemory guess_cache

    cpdef int parse(self, Tokens tokens) except -1
