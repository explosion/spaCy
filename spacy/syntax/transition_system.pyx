# cython: infer_types=True
# coding: utf-8
from __future__ import unicode_literals

from cpython.ref cimport Py_INCREF
from cymem.cymem cimport Pool
from thinc.typedefs cimport weight_t
from collections import OrderedDict, Counter
import ujson

from ..structs cimport TokenC
from .stateclass cimport StateClass
from ..typedefs cimport attr_t
from ..compat import json_dumps
from .. import util


cdef weight_t MIN_SCORE = -90000


class OracleError(Exception):
    pass


cdef void* _init_state(Pool mem, int length, void* tokens) except NULL:
    cdef StateC* st = new StateC(<const TokenC*>tokens, length)
    return <void*>st


cdef class TransitionSystem:
    def __init__(self, StringStore string_table, labels_by_action=None, min_freq=None):
        self.mem = Pool()
        self.strings = string_table
        self.n_moves = 0
        self._size = 100

        self.c = <Transition*>self.mem.alloc(self._size, sizeof(Transition))

        self.labels = {}
        if labels_by_action:
            self.initialize_actions(labels_by_action, min_freq=min_freq)
        self.root_label = self.strings.add('ROOT')
        self.init_beam_state = _init_state

    def __reduce__(self):
        return (self.__class__, (self.strings, self.labels), None, None)

    def init_batch(self, docs):
        cdef StateClass state
        states = []
        offset = 0
        for doc in docs:
            state = StateClass(doc, offset=offset)
            self.initialize_state(state.c)
            states.append(state)
            offset += len(doc)
        return states

    def get_oracle_sequence(self, doc, GoldParse gold):
        cdef Pool mem = Pool()
        costs = <float*>mem.alloc(self.n_moves, sizeof(float))
        is_valid = <int*>mem.alloc(self.n_moves, sizeof(int))

        cdef StateClass state = StateClass(doc, offset=0)
        self.initialize_state(state.c)
        history = []
        while not state.is_final():
            self.set_costs(is_valid, costs, state, gold)
            for i in range(self.n_moves):
                if is_valid[i] and costs[i] <= 0:
                    action = self.c[i]
                    history.append(i)
                    action.do(state.c, action.label)
                    break
            else:
                print(gold.words)
                print(gold.ner)
                print(history)
                raise ValueError("Could not find gold move")
        return history

    cdef int initialize_state(self, StateC* state) nogil:
        pass

    cdef int finalize_state(self, StateC* state) nogil:
        pass

    def finalize_doc(self, doc):
        pass

    def preprocess_gold(self, GoldParse gold):
        raise NotImplementedError

    def is_gold_parse(self, StateClass state, GoldParse gold):
        raise NotImplementedError

    cdef Transition lookup_transition(self, object name) except *:
        raise NotImplementedError

    cdef Transition init_transition(self, int clas, int move, attr_t label) except *:
        raise NotImplementedError

    def is_valid(self, StateClass stcls, move_name):
        action = self.lookup_transition(move_name)
        if action.move == 0:
            return False
        return action.is_valid(stcls.c, action.label)

    cdef int set_valid(self, int* is_valid, const StateC* st) nogil:
        cdef int i
        for i in range(self.n_moves):
            is_valid[i] = self.c[i].is_valid(st, self.c[i].label)

    cdef int set_costs(self, int* is_valid, weight_t* costs,
                       StateClass stcls, GoldParse gold) except -1:
        cdef int i
        self.set_valid(is_valid, stcls.c)
        cdef int n_gold = 0
        for i in range(self.n_moves):
            if is_valid[i]:
                costs[i] = self.c[i].get_cost(stcls, &gold.c, self.c[i].label)
                n_gold += costs[i] <= 0
            else:
                costs[i] = 9000
        if n_gold <= 0:
            print(gold.words)
            print(gold.ner)
            print([gold.c.ner[i].clas for i in range(gold.length)])
            print([gold.c.ner[i].move for i in range(gold.length)])
            print([gold.c.ner[i].label for i in range(gold.length)])
            print("Self labels",
                  [self.c[i].label for i in range(self.n_moves)])
            raise ValueError(
                "Could not find a gold-standard action to supervise "
                "the entity recognizer. The transition system has "
                "%d actions." % (self.n_moves))

    def get_class_name(self, int clas):
        act = self.c[clas]
        return self.move_name(act.move, act.label)

    def initialize_actions(self, labels_by_action, min_freq=None):
        self.labels = {}
        self.n_moves = 0
        for action, label_freqs in sorted(labels_by_action.items()):
            action = int(action)
            # Make sure we take a copy here, and that we get a Counter
            self.labels[action] = Counter()
            # Have to be careful here: Sorting must be stable, or our model
            # won't be read back in correctly. 
            sorted_labels = [(f, L) for L, f in label_freqs.items()]
            sorted_labels.sort()
            sorted_labels.reverse()
            for freq, label_str in sorted_labels:
                self.add_action(int(action), label_str)
                self.labels[action][label_str] = freq 

    def add_action(self, int action, label_name):
        cdef attr_t label_id
        if not isinstance(label_name, int) and \
           not isinstance(label_name, long):
            label_id = self.strings.add(label_name)
        else:
            label_id = label_name
        # Check we're not creating a move we already have, so that this is
        # idempotent
        for trans in self.c[:self.n_moves]:
            if trans.move == action and trans.label == label_id:
                return 0
        if self.n_moves >= self._size:
            self._size *= 2
            self.c = <Transition*>self.mem.realloc(self.c, self._size * sizeof(self.c[0]))
        self.c[self.n_moves] = self.init_transition(self.n_moves, action, label_id)
        assert self.c[self.n_moves].label == label_id
        self.n_moves += 1
        if self.labels.get(action, []):
            new_freq = min(self.labels[action].values())
        else:
            self.labels[action] = Counter()
            new_freq = -1
        if new_freq > 0:
            new_freq = 0
        self.labels[action][label_name] = new_freq-1
        return 1

    def to_disk(self, path, **exclude):
        with path.open('wb') as file_:
            file_.write(self.to_bytes(**exclude))

    def from_disk(self, path, **exclude):
        with path.open('rb') as file_:
            byte_data = file_.read()
        self.from_bytes(byte_data, **exclude)
        return self

    def to_bytes(self, **exclude):
        transitions = []
        serializers = {
            'moves': lambda: json_dumps(self.labels),
            'strings': lambda: self.strings.to_bytes()
        }
        return util.to_bytes(serializers, exclude)

    def from_bytes(self, bytes_data, **exclude):
        labels = {}
        deserializers = {
            'moves': lambda b: labels.update(ujson.loads(b)),
            'strings': lambda b: self.strings.from_bytes(b)
        }
        msg = util.from_bytes(bytes_data, deserializers, exclude)
        self.initialize_actions(labels)
        return self
