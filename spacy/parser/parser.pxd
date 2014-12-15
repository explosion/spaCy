from thinc.features cimport Extractor
from thinc.learner cimport LinearModel

from .arc_eager cimport TransitionSystem

from ..tokens cimport Tokens, TokenC


cdef class Parser:
    cdef object cfg
    cdef Extractor extractor
    cdef LinearModel model
    cdef TransitionSystem moves

    cpdef int parse(self, Tokens tokens) except -1
