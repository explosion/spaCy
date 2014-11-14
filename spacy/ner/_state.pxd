from cymem.cymem cimport Pool
from .structs cimport State, Entity, Move

cdef int begin_entity(State* s, label) except -1

cdef int end_entity(State* s) except -1

cdef State* init_state(Pool mem, int sent_length) except NULL
cdef int copy_state(Pool mem, State* dest, State* source) except -1

cdef bint entity_is_open(State *s) except -1

cdef bint entity_is_sunk(State *s, Move* golds) except -1
