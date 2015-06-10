from cymem.cymem cimport Pool

from thinc.typedefs cimport weight_t

from .stateclass cimport StateClass

from .transition_system cimport TransitionSystem, Transition

cdef class ArcEager(TransitionSystem):
    pass
