from cymem.cymem cimport Pool
from thinc.typedefs cimport weight_t
from collections import defaultdict

from ..structs cimport TokenC
from .stateclass cimport StateClass
from ..attrs cimport TAG, HEAD, DEP, ENT_TYPE, ENT_IOB


cdef weight_t MIN_SCORE = -90000


class OracleError(Exception):
    pass


cdef class TransitionSystem:
    def __init__(self, StringStore string_table, dict labels_by_action, _freqs=None):
        self._labels_by_action = labels_by_action
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
        self.root_label = self.strings['ROOT']
        self.freqs = {} if _freqs is None else _freqs
        for attr in (TAG, HEAD, DEP, ENT_TYPE, ENT_IOB):
            self.freqs[attr] = defaultdict(int)
            self.freqs[attr][0] = 1
        # Ensure we've seen heads. Need an official dependency length limit...
        for i in range(10024):
            self.freqs[HEAD][i] = 1
            self.freqs[HEAD][-i] = 1

    def __reduce__(self):
        return (self.__class__,
                (self.strings, self._labels_by_action, self.freqs),
                None, None)

    cdef int initialize_state(self, StateClass state) except -1:
        pass

    cdef int finalize_state(self, StateClass state) nogil:
        pass

    cdef int preprocess_gold(self, GoldParse gold) except -1:
        raise NotImplementedError

    cdef Transition lookup_transition(self, object name) except *:
        raise NotImplementedError

    cdef Transition init_transition(self, int clas, int move, int label) except *:
        raise NotImplementedError

    def is_valid(self, StateClass stcls, move_name):
        action = self.lookup_transition(move_name)
        return action.is_valid(stcls, action.label)

    cdef int set_valid(self, int* is_valid, StateClass stcls) nogil:
        cdef int i
        for i in range(self.n_moves):
            is_valid[i] = self.c[i].is_valid(stcls, self.c[i].label)

    cdef int set_costs(self, int* is_valid, int* costs,
                       StateClass stcls, GoldParse gold) except -1:
        cdef int i
        self.set_valid(is_valid, stcls)
        for i in range(self.n_moves):
            if is_valid[i]:
                costs[i] = self.c[i].get_cost(stcls, &gold.c, self.c[i].label)
            else:
                costs[i] = 9000
