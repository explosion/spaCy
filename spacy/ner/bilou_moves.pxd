from cymem.cymem cimport Pool

from thinc.typedefs cimport class_t
from thinc.typedefs cimport weight_t

from .structs cimport State, Move


cpdef enum ActionType:
    MISSING
    BEGIN
    IN
    LAST
    UNIT
    OUT
    N_ACTIONS


cdef int set_accept_if_oracle(Move* moves, Move* golds, int n, State* s) except 0

cdef int set_accept_if_valid(Move* moves, int n, State* s) except 0

cdef Move* best_accepted(Move* moves, weight_t* scores, int n) except NULL

cdef int transition(State *s, Move* m) except -1

cdef int fill_moves(Move* moves, list tag_names) except -1
