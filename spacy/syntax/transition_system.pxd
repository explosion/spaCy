from cymem.cymem cimport Pool
from thinc.typedefs cimport weight_t

from ..typedefs cimport attr_t
from ..structs cimport TokenC
from ..gold cimport GoldParse
from ..gold cimport GoldParseC
from ..strings cimport StringStore

from .stateclass cimport StateClass
from ._state cimport StateC


cdef struct Transition:
    int clas
    int move
    attr_t label

    weight_t score

    bint (*is_valid)(const StateC* state, attr_t label) nogil
    weight_t (*get_cost)(StateClass state, const GoldParseC* gold, attr_t label) nogil
    int (*do)(StateC* state, attr_t label) nogil


ctypedef weight_t (*get_cost_func_t)(StateClass state, const GoldParseC* gold,
        attr_tlabel) nogil
ctypedef weight_t (*move_cost_func_t)(StateClass state, const GoldParseC* gold) nogil
ctypedef weight_t (*label_cost_func_t)(StateClass state, const GoldParseC*
        gold, attr_t label) nogil

ctypedef int (*do_func_t)(StateC* state, attr_t label) nogil

ctypedef void* (*init_state_t)(Pool mem, int length, void* tokens) except NULL

ctypedef int (*del_state_t)(Pool mem, void* state, void* extra_args) except -1

cdef class TransitionSystem:
    cdef Pool mem
    cdef StringStore strings
    cdef Transition* c
    cdef readonly int n_moves
    cdef int _size
    cdef public attr_t root_label
    cdef public freqs
    cdef init_state_t init_beam_state
    cdef del_state_t del_beam_state
    cdef public object labels

    cdef int initialize_state(self, StateC* state) nogil
    cdef int finalize_state(self, StateC* state) nogil

    cdef Transition lookup_transition(self, object name) except *

    cdef Transition init_transition(self, int clas, int move, attr_t label) except *

    cdef int set_valid(self, int* output, const StateC* st) nogil

    cdef int set_costs(self, int* is_valid, weight_t* costs,
                       StateClass state, GoldParse gold) except -1
