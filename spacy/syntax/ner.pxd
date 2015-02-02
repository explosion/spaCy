from cymem.cymem cimport Pool

from thinc.typedefs cimport weight_t


from ._state cimport State 


cdef struct Transition:
    int clas
    int move
    int label
    int cost
    weight_t score


cdef class TransitionSystem:
    cdef Pool mem
    cdef readonly int n_moves
    cdef dict label_ids

    cdef const Transition* _moves

    cdef Transition best_valid(self, const weight_t* scores, const State* s) except *
    cdef Transition best_gold(self, Transition* guess, const weight_t* scores,
                              const State* s,
                              const int* gold_heads, const int* gold_labels) except *
    cdef int transition(self, State *s, const Transition* t) except -1
