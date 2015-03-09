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
        self.n_moves = sum(len(labels) for labels in labels_by_action.values())
        moves = <Transition*>self.mem.alloc(self.n_moves, sizeof(Transition))
        cdef int i = 0
        cdef int label_id
        self.label_ids = {'ROOT': 0}
        for action, label_strs in sorted(labels_by_action.items()):
            for label_str in sorted(label_strs):
                label_str = unicode(label_str)
                label_id = self.label_ids.setdefault(label_str, len(self.label_ids))
                moves[i] = self.init_transition(i, int(action), label_id)
                i += 1
        self.label_ids['MISSING'] = -1
        self.c = moves

    cdef int preprocess_gold(self, GoldParse gold) except -1:
        raise NotImplementedError

    cdef Transition lookup_transition(self, object name) except *:
        raise NotImplementedError

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
        assert score > MIN_SCORE
        return best


#cdef class PyState:
#    """Provide a Python class for testing purposes."""
#    def __init__(self, GoldParse gold):
#        self.mem = Pool()
#        self.system = EntityRecognition(labels)
#        self._state = init_state(self.mem, tokens, gold.length)
#
#    def transition(self, name):
#        cdef const Transition* trans = self._transition_by_name(name)
#        trans.do(trans, self._state)
#
#    def is_valid(self, name):
#        cdef const Transition* trans = self._transition_by_name(name)
#        return _is_valid(trans.move, trans.label, self._state)
#
#    def is_gold(self, name):
#        cdef const Transition* trans = self._transition_by_name(name)
#        return _get_const(trans, self._state, self._gold)
#
#    property ent:
#        def __get__(self):
#            pass
#
#    property n_ents:
#        def __get__(self):
#            pass
#
#    property i:
#        def __get__(self):
#            pass
#
#    property open_entity:
#        def __get__(self):
#            return entity_is_open(self._s)
