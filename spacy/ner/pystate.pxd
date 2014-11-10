from cymem.cymem cimport Pool

from .moves cimport Move
from ._state cimport State


cdef class PyState:
    cdef Pool mem
    cdef readonly list entity_types
    cdef readonly int n_classes
    cdef readonly dict moves_by_name
    
    cdef Move* _moves
    cdef Move* _golds
    cdef State* _s

    cdef Move* _get_move(self, unicode move_name) except NULL
