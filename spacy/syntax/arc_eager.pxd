from cymem.cymem cimport Pool

from thinc.typedefs cimport weight_t


from ._state cimport State
from .transition_system cimport TransitionSystem, Transition

cdef class ArcEager(TransitionSystem):
    pass
