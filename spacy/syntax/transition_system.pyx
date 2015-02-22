from cymem.cymem cimport Pool
from ._state cimport State
from ..structs cimport TokenC
from thinc.typedefs cimport weight_t


cdef weight_t MIN_SCORE = -90000


class OracleError(Exception):
    pass


cdef class TransitionSystem:
    def __init__(self, dict labels_by_action):
        self.mem = Pool()
        self.n_moves = sum(len(labels) for labels in labels_by_action.items())
        moves = <Transition*>self.mem.alloc(self.n_moves, sizeof(Transition))
        cdef int i = 0
        self.label_ids = {}
        for action, label_strs in sorted(labels_by_action.items()):
            label_str = unicode(label_str)
            label_id = self.label_ids.setdefault(label_str, len(self.label_ids))
            moves[i] = self.init_transition(i, action, label_id)
            i += 1
        self.c = moves

    cdef Transition init_transition(self, int clas, int move, int label) except *:
        raise NotImplementedError

    cdef Transition best_valid(self, const weight_t* scores, const State* s) except *:
        raise NotImplementedError

    cdef Transition best_gold(self, const weight_t* scores, const State* s,
                              GoldParse gold) except *:
        cdef Transition best
        cdef weight_t score = MIN_SCORE
        cdef int i
        for i in range(self.n_moves):
            if scores[i] > score and self.c[i].get_cost(&self.c[i], s, gold) == 0:
                best = self.c[i]
                score = scores[i]
        return best
