from thinc.search cimport Beam

from .._ml cimport Model

from .arc_eager cimport TransitionSystem

from ..tokens.doc cimport Doc
from ..structs cimport TokenC
from thinc.api cimport Example, ExampleC
from .stateclass cimport StateClass


cdef class Parser:
    cdef readonly object cfg
    cdef readonly Model model
    cdef readonly TransitionSystem moves

    cdef void parse(self, StateClass stcls, ExampleC eg) nogil
