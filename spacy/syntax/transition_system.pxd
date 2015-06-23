from cymem.cymem cimport Pool
from thinc.typedefs cimport weight_t

from ..structs cimport TokenC
from ..gold cimport GoldParse
from ..gold cimport GoldParseC
from ..strings cimport StringStore

from .stateclass cimport StateClass


cdef struct Transition:
    int clas
    int move
    int label

    weight_t score

    bint (*is_valid)(StateClass state, int label) nogil
    int (*get_cost)(StateClass state, const GoldParseC* gold, int label) nogil
    int (*do)(StateClass state, int label) nogil


ctypedef int (*get_cost_func_t)(StateClass state, const GoldParseC* gold, int label) nogil
ctypedef int (*move_cost_func_t)(StateClass state, const GoldParseC* gold) nogil
ctypedef int (*label_cost_func_t)(StateClass state, const GoldParseC* gold, int label) nogil

ctypedef int (*do_func_t)(StateClass state, int label) nogil


cdef class TransitionSystem:
    cdef Pool mem
    cdef StringStore strings
    cdef const Transition* c
    cdef bint* _is_valid
    cdef readonly int n_moves

    cdef int initialize_state(self, StateClass state) except -1
    cdef int finalize_state(self, StateClass state) except -1

    cdef int preprocess_gold(self, GoldParse gold) except -1

    cdef Transition lookup_transition(self, object name) except *

    cdef Transition init_transition(self, int clas, int move, int label) except *

    cdef int set_valid(self, bint* output, StateClass state) except -1
    
    cdef int set_costs(self, int* output, StateClass state, GoldParse gold) except -1

    cdef Transition best_valid(self, const weight_t* scores, StateClass stcls) except *

    cdef Transition best_gold(self, const weight_t* scores, StateClass state,
                              GoldParse gold) except *
