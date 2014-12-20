from cymem.cymem cimport Pool

from thinc.typedefs cimport weight_t


from ._state cimport State 


cdef struct Transition:
    int move
    int label


cdef class TransitionSystem:
    cdef Pool mem
    cdef readonly int n_moves
    cdef dict label_ids

    cdef const Transition* _moves

    cdef Transition best_valid(self, const weight_t* scores, const State* s) except -1
    cdef Transition best_gold(self, const weight_t* scores, const State* s,
                              int* gold_heads, int* gold_labels) except -1
    cdef int transition(self, State *s, const Transition* t) except -1
