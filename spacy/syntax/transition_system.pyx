# cython: infer_types=True
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
        self.mem = Pool()
        self.strings = string_table
        self.n_moves = 0
        self._size = 100
        
        self.c = <Transition*>self.mem.alloc(self._size, sizeof(Transition))
        
        for action, label_strs in sorted(labels_by_action.items()):
            for label_str in sorted(label_strs):
                self.add_action(int(action), label_str)
        
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
        labels_by_action = {}
        cdef Transition t
        for trans in self.c[:self.n_moves]:
            label_str = self.strings[trans.label]
            labels_by_action.setdefault(trans.move, []).append(label_str)
        return (self.__class__,
                (self.strings, labels_by_action, self.freqs),
                None, None)

    cdef int initialize_state(self, StateC* state) nogil:
        pass

    cdef int finalize_state(self, StateC* state) nogil:
        pass

    def finalize_doc(self, doc):
        pass

    cdef int preprocess_gold(self, GoldParse gold) except -1:
        raise NotImplementedError

    cdef Transition lookup_transition(self, object name) except *:
        raise NotImplementedError

    cdef Transition init_transition(self, int clas, int move, int label) except *:
        raise NotImplementedError

    def is_valid(self, StateClass stcls, move_name):
        action = self.lookup_transition(move_name)
        return action.is_valid(stcls.c, action.label)

    cdef int set_valid(self, int* is_valid, const StateC* st) nogil:
        cdef int i
        for i in range(self.n_moves):
            is_valid[i] = self.c[i].is_valid(st, self.c[i].label)

    cdef int set_costs(self, int* is_valid, weight_t* costs,
                       StateClass stcls, GoldParse gold) except -1:
        cdef int i
        self.set_valid(is_valid, stcls.c)
        for i in range(self.n_moves):
            if is_valid[i]:
                costs[i] = self.c[i].get_cost(stcls, &gold.c, self.c[i].label)
            else:
                costs[i] = 9000

    def add_action(self, int action, label):
        if not isinstance(label, int):
            label = self.strings[label]
        # Check we're not creating a move we already have, so that this is
        # idempotent
        for trans in self.c[:self.n_moves]:
            if trans.move == action and trans.label == label:
                return 0
        if self.n_moves >= self._size:
            self._size *= 2
            self.c = <Transition*>self.mem.realloc(self.c, self._size * sizeof(self.c[0]))
        
        self.c[self.n_moves] = self.init_transition(self.n_moves, action, label)
        self.n_moves += 1
        return 1
