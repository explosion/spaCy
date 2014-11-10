from ._state cimport init_state
from ._state cimport entity_is_open
from .moves cimport fill_moves
from .moves cimport transition
from .moves import get_n_moves
from .moves import ACTION_NAMES


cdef class PyState:
    def __init__(self, tag_names, n_tokens):
        self.mem = Pool()
        self.entity_types = tag_names
        self.n_classes = get_n_moves(len(self.entity_types))
        assert self.n_classes != 0
        self._moves = <Move*>self.mem.alloc(self.n_classes, sizeof(Move))
        fill_moves(self._moves, len(self.entity_types))
        self._s = init_state(self.mem, n_tokens)
        self.moves_by_name = {}
        for i in range(self.n_classes):
            m = &self._moves[i]
            action_name = ACTION_NAMES[m.action]
            tag_name = tag_names[m.label]
            self.moves_by_name['%s-%s' % (action_name, tag_name)] = i

    def transition(self, unicode move_name):
        cdef int m_i = self.moves_by_name[move_name]
        cdef Move* m = &self._moves[m_i]
        transition(self._s, m)

    def is_valid(self, unicode move_name):
        pass

    def is_gold(self, unicode move_name):
        pass

    property ent:
        def __get__(self):
            return self._s.ents[self._s.j]

    property n_ents:
        def __get__(self):
            return self._s.j + 1

    property i:
        def __get__(self):
            return self._s.i

    property open_entity:
        def __get__(self):
            return entity_is_open(self._s)


