from cymem.cymem cimport Pool
from thinc.typedefs cimport weight_t

from ..structs cimport TokenC
from ._state cimport State
from ..gold cimport GoldParse
from ..gold cimport GoldParseC
from ..strings cimport StringStore


cdef struct Transition:
    int clas
    int move
    int label

    weight_t score

    bint (*is_valid)(const State* state, int label) except -1
    int (*get_cost)(const State* state, const GoldParseC* gold, int label) except -1
    int (*do)(State* state, int label) except -1


ctypedef int (*get_cost_func_t)(const State* state, const GoldParseC* gold, int label) except -1

ctypedef int (*do_func_t)(State* state, int label) except -1


cdef class TransitionSystem:
    cdef Pool mem
    cdef StringStore strings
    cdef const Transition* c
    cdef bint* _is_valid
    cdef readonly int n_moves

    cdef int initialize_state(self, State* state) except -1
    cdef int finalize_state(self, State* state) except -1

    cdef int preprocess_gold(self, GoldParse gold) except -1

    cdef Transition lookup_transition(self, object name) except *

    cdef Transition init_transition(self, int clas, int move, int label) except *

    cdef int set_valid(self, bint* output, const State* state) except -1
    
    cdef int set_costs(self, int* output, const State* state, GoldParse gold) except -1

    cdef Transition best_valid(self, const weight_t* scores, const State* state) except *

    cdef Transition best_gold(self, const weight_t* scores, const State* state,
                              GoldParse gold) except *


#cdef class PyState:
#    """Provide a Python class for testing purposes."""
#    cdef Pool mem
#    cdef TransitionSystem system
#    cdef State* _state
