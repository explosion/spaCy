from cymem.cymem cimport Pool
from thinc.typedefs cimport weight_t

from ..structs cimport TokenC
from ..gold cimport GoldParse
from ..gold cimport GoldParseC
from ..strings cimport StringStore

from .stateclass cimport StateClass
from ._state cimport StateC


cdef struct Transition:
    int clas
    int move
    int label

    weight_t score

    bint (*is_valid)(const StateC* state, int label) nogil
    weight_t (*get_cost)(StateClass state, const GoldParseC* gold, int label) nogil
    int (*do)(StateC* state, int label) nogil


ctypedef weight_t (*get_cost_func_t)(StateClass state, const GoldParseC* gold, int label) nogil
ctypedef weight_t (*move_cost_func_t)(StateClass state, const GoldParseC* gold) nogil
ctypedef weight_t (*label_cost_func_t)(StateClass state, const GoldParseC* gold, int label) nogil

ctypedef int (*do_func_t)(StateC* state, int label) nogil


cdef class TransitionSystem:
    cdef Pool mem
    cdef StringStore strings
    cdef Transition* c
    cdef readonly int n_moves
    cdef int _size
    cdef public int root_label
    cdef public freqs

    cdef int initialize_state(self, StateC* state) nogil
    cdef int finalize_state(self, StateC* state) nogil

    cdef int preprocess_gold(self, GoldParse gold) except -1

    cdef Transition lookup_transition(self, object name) except *

    cdef Transition init_transition(self, int clas, int move, int label) except *

    cdef int set_valid(self, int* output, const StateC* st) nogil

    cdef int set_costs(self, int* is_valid, weight_t* costs,
                       StateClass state, GoldParse gold) except -1
