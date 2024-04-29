# cython: infer_types=True
# cython: profile=False
from __future__ import print_function

from cymem.cymem cimport Pool

from collections import Counter

import srsly

from ...structs cimport TokenC
from ...typedefs cimport attr_t, weight_t
from .stateclass cimport StateClass

from ... import util
from ...errors import Errors


cdef weight_t MIN_SCORE = -90000


class OracleError(Exception):
    pass


cdef void* _init_state(Pool mem, int length, void* tokens) except NULL:
    cdef StateC* st = new StateC(<const TokenC*>tokens, length)
    return <void*>st


cdef int _del_state(Pool mem, void* state, void* x) except -1:
    cdef StateC* st = <StateC*>state
    del st


cdef class TransitionSystem:
    def __init__(
        self,
        StringStore string_table,
        labels_by_action=None,
        min_freq=None,
        incorrect_spans_key=None
    ):
        self.cfg = {"neg_key": incorrect_spans_key}
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
        self.del_beam_state = _del_state

    def __reduce__(self):
        # TODO: This loses the 'cfg'
        return (self.__class__, (self.strings, self.labels), None, None)

    @property
    def neg_key(self):
        return self.cfg.get("neg_key")

    def init_batch(self, docs):
        cdef StateClass state
        states = []
        offset = 0
        for doc in docs:
            state = StateClass(doc, offset=offset)
            states.append(state)
            offset += len(doc)
        return states

    def get_oracle_sequence(self, Example example, _debug=False):
        states, golds, _ = self.init_gold_batch([example])
        if not states:
            return []
        state = states[0]
        gold = golds[0]
        if _debug:
            return self.get_oracle_sequence_from_state(state, gold, _debug=example)
        else:
            return self.get_oracle_sequence_from_state(state, gold)

    def get_oracle_sequence_from_state(self, StateClass state, gold, _debug=None):
        cdef Pool mem = Pool()
        # n_moves should not be zero at this point, but make sure to avoid zero-length mem alloc
        assert self.n_moves > 0
        costs = <float*>mem.alloc(self.n_moves, sizeof(float))
        is_valid = <int*>mem.alloc(self.n_moves, sizeof(int))

        history = []
        debug_log = []
        while not state.is_final():
            self.set_costs(is_valid, costs, state.c, gold)
            for i in range(self.n_moves):
                if is_valid[i] and costs[i] <= 0:
                    action = self.c[i]
                    history.append(i)
                    if _debug:
                        s0 = state.S(0)
                        b0 = state.B(0)
                        example = _debug
                        debug_log.append(" ".join((
                            self.get_class_name(i),
                            "S0=", (example.x[s0].text if s0 >= 0 else "__"),
                            "B0=", (example.x[b0].text if b0 >= 0 else "__"),
                            "S0 head?", str(state.has_head(state.S(0))),
                        )))
                    action.do(state.c, action.label)
                    break
            else:
                if _debug:
                    example = _debug
                    print("Actions")
                    for i in range(self.n_moves):
                        print(self.get_class_name(i))
                    print("Gold")
                    for token in example.y:
                        print(token.text, token.dep_, token.head.text)
                    s0 = state.S(0)
                    b0 = state.B(0)
                    debug_log.append(" ".join((
                        "?",
                        "S0=", (example.x[s0].text if s0 >= 0 else "-"),
                        "B0=", (example.x[b0].text if b0 >= 0 else "-"),
                        "S0 head?", str(state.has_head(state.S(0))),
                    )))
                    print("\n".join(debug_log))
                raise ValueError(Errors.E024)
        return history

    def apply_transition(self, StateClass state, name):
        if not self.is_valid(state, name):
            raise ValueError(Errors.E170.format(name=name))
        action = self.lookup_transition(name)
        action.do(state.c, action.label)

    cdef Transition lookup_transition(self, object name) except *:
        raise NotImplementedError

    cdef Transition init_transition(self, int clas, int move, attr_t label) except *:
        raise NotImplementedError

    def is_valid(self, StateClass stcls, move_name):
        action = self.lookup_transition(move_name)
        return action.is_valid(stcls.c, action.label)

    cdef int set_valid(self, int* is_valid, const StateC* st) nogil:
        cdef int i
        for i in range(self.n_moves):
            is_valid[i] = self.c[i].is_valid(st, self.c[i].label)

    cdef int set_costs(self, int* is_valid, weight_t* costs,
                       const StateC* state, gold) except -1:
        raise NotImplementedError

    def get_class_name(self, int clas):
        act = self.c[clas]
        return self.move_name(act.move, act.label)

    def initialize_actions(self, labels_by_action, min_freq=None):
        self.labels = {}
        self.n_moves = 0
        added_labels = []
        added_actions = {}
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
                if freq < 0:
                    added_labels.append((freq, label_str))
                    added_actions.setdefault(label_str, []).append(action)
                else:
                    self.add_action(int(action), label_str)
                    self.labels[action][label_str] = freq
        added_labels.sort(reverse=True)
        for freq, label_str in added_labels:
            for action in added_actions[label_str]:
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
        self.n_moves += 1
        # Add the new (action, label) pair, making up a frequency for it if
        # necessary. To preserve sort order, the frequency needs to be lower
        # than previous frequencies.
        if self.labels.get(action, []):
            new_freq = min(self.labels[action].values())
        else:
            self.labels[action] = Counter()
            new_freq = -1
        if new_freq > 0:
            new_freq = 0
        self.labels[action][label_name] = new_freq-1
        return 1

    def to_disk(self, path, **kwargs):
        with path.open('wb') as file_:
            file_.write(self.to_bytes(**kwargs))

    def from_disk(self, path, **kwargs):
        with path.open('rb') as file_:
            byte_data = file_.read()
        self.from_bytes(byte_data, **kwargs)
        return self

    def to_bytes(self, exclude=tuple()):
        serializers = {
            'moves': lambda: srsly.json_dumps(self.labels),
            'strings': lambda: self.strings.to_bytes(),
            'cfg': lambda: self.cfg
        }
        return util.to_bytes(serializers, exclude)

    def from_bytes(self, bytes_data, exclude=tuple()):
        # We're adding a new field, 'cfg', here and we don't want to break
        # previous models that don't have it.
        msg = srsly.msgpack_loads(bytes_data)
        labels = {}
        if 'moves' not in exclude:
            labels.update(srsly.json_loads(msg['moves']))
        if 'strings' not in exclude:
            self.strings.from_bytes(msg['strings'])
        if 'cfg' not in exclude and 'cfg' in msg:
            self.cfg.update(msg['cfg'])
        self.initialize_actions(labels)
        return self
