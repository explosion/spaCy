from cymem.cymem cimport Pool

from thinc.typedefs cimport weight_t


from ._state cimport State 


cdef struct Transition:
    int move
    int label


cdef class TransitionSystem:
    cdef Pool mem
    cdef readonly int n_moves

    cdef const Transition* _moves

    cdef int best_valid(self, const weight_t* scores, const State* s) except -1
    cdef int best_gold(self, const weight_t* scores, const State* s,
                       list gold_heads, list gold_labels) except -1
    cdef int transition(self, State *s, const int clas) except -1
