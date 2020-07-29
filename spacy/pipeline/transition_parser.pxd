from cymem.cymem cimport Pool

from ..typedefs cimport attr_t, weight_t
from ..strings cimport StringStore
from ..vocab cimport Vocab
from .pipe cimport Pipe
from ._parser_internals.stateclass cimport StateClass
from ._parser_internals._state cimport StateC
from ..ml.parser_model cimport WeightsC, ActivationsC, SizesC
from ..gold.example cimport Example


cdef class Parser(Pipe):
    cdef readonly Vocab vocab
    cdef public object model
    cdef public object _rehearsal_model
    cdef readonly TransitionSystem moves
    cdef readonly object cfg
    cdef public object _multitasks

    cdef void _parseC(self, StateC** states,
            WeightsC weights, SizesC sizes) nogil

    cdef void c_transition_batch(self, StateC** states, const float* scores,
            int nr_class, int batch_size) nogil


cdef struct Transition:
    int clas
    int move
    attr_t label

    weight_t score

    bint (*is_valid)(const StateC* state, attr_t label) nogil
    weight_t (*get_cost)(StateClass state, const void* gold, attr_t label) nogil
    int (*do)(StateC* state, attr_t label) nogil


ctypedef weight_t (*get_cost_func_t)(StateClass state, const void* gold,
        attr_tlabel) nogil
ctypedef weight_t (*move_cost_func_t)(StateClass state, const void* gold) nogil
ctypedef weight_t (*label_cost_func_t)(StateClass state, const void*
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
    cdef public object labels

    cdef int initialize_state(self, StateC* state) nogil
    cdef int finalize_state(self, StateC* state) nogil

    cdef Transition lookup_transition(self, object name) except *

    cdef Transition init_transition(self, int clas, int move, attr_t label) except *

    cdef int set_valid(self, int* output, const StateC* st) nogil

    cdef int set_costs(self, int* is_valid, weight_t* costs,
                       StateClass state, gold) except -1
