from cymem.cymem cimport Pool

from .moves cimport Move
from ._state cimport State


cdef class PyState:
    cdef Pool mem
    cdef readonly list entity_types
    cdef readonly int n_classes
    cdef readonly dict moves_by_name
    
    cdef Move* _moves
    cdef State* _s
