from .arc_eager cimport TransitionSystem
from ._state cimport StateC
from ..structs cimport TokenC

from thinc.base cimport Model
from thinc.linalg cimport *


cdef class Parser:
    cdef readonly Model model
    cdef readonly TransitionSystem moves
    cdef int _projectivize

    cdef int parseC(self, TokenC* tokens, int length, int nr_feat, int nr_class) with gil
