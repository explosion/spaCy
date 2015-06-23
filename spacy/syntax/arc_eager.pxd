from cymem.cymem cimport Pool

from thinc.typedefs cimport weight_t

from .stateclass cimport StateClass

from .transition_system cimport TransitionSystem, Transition
from ..gold cimport GoldParseC


cdef class ArcEager(TransitionSystem):
    pass


cdef int push_cost(StateClass stcls, const GoldParseC* gold, int target) nogil
cdef int arc_cost(StateClass stcls, const GoldParseC* gold, int head, int child) nogil

