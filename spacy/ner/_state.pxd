from cymem.cymem cimport Pool
from .moves cimport Move


cdef struct Entity:
    int start
    int end
    int label


cdef struct State:
    Entity curr
    Entity* ents
    int* tags
    int i
    int j
    int length


cdef int begin_entity(State* s, label) except -1

cdef int end_entity(State* s) except -1

cdef State* init_state(Pool mem, int sent_length) except NULL

cdef bint entity_is_open(State *s) except -1

cdef bint entity_is_sunk(State *s, Move* golds) except -1
