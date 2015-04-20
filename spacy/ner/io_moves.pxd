from cymem.cymem cimport Pool

from thinc.typedefs cimport class_t
from thinc.typedefs cimport weight_t

from .structs cimport State, Move


cpdef enum ActionType:
    MISSING
    SHIFT
    REDUCE
    OUT
    N_ACTIONS


cdef int set_accept_if_oracle(Move* moves, int n, State* s,
                              int* g_starts, int* g_ends, int* g_labels) except 0

cdef int set_accept_if_valid(Move* moves, int n, State* s) except 0

cdef Move* best_accepted(Move* moves, weight_t* scores, int n) except NULL

cdef int transition(State *s, Move* m) except -1

cdef int fill_moves(Move* moves, int n, list entity_types) except -1
