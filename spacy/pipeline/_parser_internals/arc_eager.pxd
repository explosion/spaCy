from ._state cimport StateC
from ...typedefs cimport weight_t, attr_t
from .transition_system cimport Transition, TransitionSystem


cdef class ArcEager(TransitionSystem):
    pass


cdef weight_t push_cost(const StateC* state, const void* _gold, int target) nogil
cdef weight_t arc_cost(const StateC* state, const void* _gold, int head, int child) nogil
