from thinc.search cimport Beam

from .._ml cimport Model

from .arc_eager cimport TransitionSystem

from ..tokens.doc cimport Doc
from ..structs cimport TokenC


cdef class Parser:
    cdef readonly object cfg
    cdef readonly Model model
    cdef readonly TransitionSystem moves
