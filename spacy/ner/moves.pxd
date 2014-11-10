from cymem.cymem cimport Pool

from thinc.typedefs cimport class_t
from thinc.typedefs cimport weight_t

from ._state cimport State

cpdef enum ActionType:
    BEGIN
    IN
    LAST
    UNIT
    OUT
    N_ACTIONS


cdef struct Move:
    class_t clas
    int action
    int label
    bint accept


cdef int set_accept_if_oracle(Move* moves, Move* golds, int n, State* s) except 0

cdef int set_accept_if_valid(Move* moves, int n, State* s) except 0

cdef Move* best_accepted(Move* moves, weight_t* scores, int n) except NULL

cdef int transition(State *s, Move* m) except -1

cdef int fill_moves(Move* moves, int n_tags) except -1
