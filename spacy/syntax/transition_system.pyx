from cymem.cymem cimport Pool
from ._state cimport State
from ..structs cimport TokenC
from thinc.typedefs cimport weight_t

from .stateclass cimport StateClass


cdef weight_t MIN_SCORE = -90000


class OracleError(Exception):
    pass


cdef class TransitionSystem:
    def __init__(self, StringStore string_table, dict labels_by_action):
        self.mem = Pool()
        self.n_moves = sum(len(labels) for labels in labels_by_action.values())
        self._is_valid = <bint*>self.mem.alloc(self.n_moves, sizeof(bint))
        moves = <Transition*>self.mem.alloc(self.n_moves, sizeof(Transition))
        cdef int i = 0
        cdef int label_id
        self.strings = string_table
        for action, label_strs in sorted(labels_by_action.items()):
            for label_str in sorted(label_strs):
                label_id = self.strings[unicode(label_str)] if label_str else 0
                moves[i] = self.init_transition(i, int(action), label_id)
                i += 1
        self.c = moves

    cdef int initialize_state(self, State* state) except -1:
        pass

    cdef int finalize_state(self, StateClass state) except -1:
        pass

    cdef int preprocess_gold(self, GoldParse gold) except -1:
        raise NotImplementedError

    cdef Transition lookup_transition(self, object name) except *:
        raise NotImplementedError

    cdef Transition init_transition(self, int clas, int move, int label) except *:
        raise NotImplementedError

    cdef Transition best_valid(self, const weight_t* scores, StateClass s) except *:
        raise NotImplementedError
    
    cdef int set_valid(self, bint* output, StateClass state) except -1:
        raise NotImplementedError

    cdef int set_costs(self, int* output, StateClass stcls, GoldParse gold) except -1:
        cdef int i
        for i in range(self.n_moves):
            if self.c[i].is_valid(stcls, self.c[i].label):
                output[i] = self.c[i].get_cost(stcls, &gold.c, self.c[i].label)
            else:
                output[i] = 9000

    cdef Transition best_gold(self, const weight_t* scores, StateClass stcls,
                              GoldParse gold) except *:
        cdef Transition best
        cdef weight_t score = MIN_SCORE
        cdef int i
        for i in range(self.n_moves):
            if self.c[i].is_valid(stcls, self.c[i].label):
                cost = self.c[i].get_cost(stcls, &gold.c, self.c[i].label)
                if scores[i] > score and cost == 0:
                    best = self.c[i]
                    score = scores[i]
        assert score > MIN_SCORE
        return best
