from .stateclass cimport StateClass
from ...typedefs cimport weight_t, attr_t
from .transition_system cimport Transition, TransitionSystem


cdef class ArcEager(TransitionSystem):
    pass


cdef weight_t push_cost(StateClass stcls, const void* _gold, int target) nogil
cdef weight_t arc_cost(StateClass stcls, const void* _gold, int head, int child) nogil
