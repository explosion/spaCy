from __future__ import unicode_literals

from ._state cimport init_state
from ._state cimport entity_is_open
from .bilou_moves cimport fill_moves
from .bilou_moves cimport transition
from .bilou_moves cimport set_accept_if_valid, set_accept_if_oracle
from .bilou_moves import get_n_moves
from .bilou_moves import ACTION_NAMES


cdef class PyState:
    def __init__(self, tag_names, n_tokens):
        self.mem = Pool()
        self.tag_names = tag_names
        self.n_classes = len(tag_names)
        assert self.n_classes != 0
        self._moves = <Move*>self.mem.alloc(self.n_classes, sizeof(Move))
        fill_moves(self._moves, tag_names)
        self._s = init_state(self.mem, n_tokens)
        self._golds = <Move*>self.mem.alloc(n_tokens, sizeof(Move))

    cdef Move* _get_move(self, unicode move_name) except NULL:
        return &self._moves[self.tag_names.index(move_name)]

    def set_golds(self, list gold_names):
        cdef Move* m
        for i, name in enumerate(gold_names):
            m = self._get_move(name)
            self._golds[i] = m[0]

    def transition(self, unicode move_name):
        cdef Move* m = self._get_move(move_name)
        transition(self._s, m)

    def is_valid(self, unicode move_name):
        cdef Move* m = self._get_move(move_name)
        set_accept_if_valid(self._moves, self.n_classes, self._s)
        return m.accept

    def is_gold(self, unicode move_name):
        cdef Move* m = self._get_move(move_name)
        set_accept_if_oracle(self._moves, self._golds, self.n_classes, self._s)
        return m.accept

    property ent:
        def __get__(self):
            return self._s.curr

    property n_ents:
        def __get__(self):
            return self._s.j

    property i:
        def __get__(self):
            return self._s.i

    property open_entity:
        def __get__(self):
            return entity_is_open(self._s)
