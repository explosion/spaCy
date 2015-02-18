from cymem.cymem cimport Pool
from ._state cimport State
from ..structs cimport TokenC
from thinc.typedefs cimport weight_t


cdef weight_t MIN_SCORE = -90000

cdef class TransitionSystem:
    cdef Pool mem
    cdef const Transition* c

    def __init__(self, dict move_types):
        entries = []
        for move, labels in move_types.items():
            entries.extend((move, label) for label in labels)
        entries.sort()
        moves = <Transition*>self.mem.alloc(len(entries), sizeof(Transition))
        for i, (move, label_str) in enumerate(entries):
            moves[i].move = move
            moves[i].label = self.label_ids.setdefault(label_str, len(self.label_ids))
            moves[i].clas
    
    cdef const Transition best_valid(self, const weight_t* scores,
                                     const State* s) except *:
        cdef int best = -1
        cdef weight_t score = MIN_SCORE
        cdef int i
        for i in range(self.n_moves):
            if scores[i] > score and self.c[i].is_valid(&self.c[i], s):
                best = i
                score = scores[i]
        return self.c[best]

    cdef const Transition best_gold(self, const weight_t* scores, const State* s,
                                    const TokenC* gold) except *:
        cdef int best = -1
        cdef weight_t score = MIN_SCORE
        cdef int i
        for i in range(self.n_moves):
            if scores[i] > score and self.c[i].get_cost(&self.c[i], s, gold) == 0:
                best = i
                score = scores[i]
        return self.c[best]
