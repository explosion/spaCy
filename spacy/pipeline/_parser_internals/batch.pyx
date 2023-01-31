from typing import Any

TransitionSystem = Any  # TODO

cdef class Batch:
    def advance(self, scores):
        raise NotImplementedError

    def get_states(self):
        raise NotImplementedError

    @property
    def is_done(self):
        raise NotImplementedError

    def get_unfinished_states(self):
        raise NotImplementedError

    def __getitem__(self, i):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError


class GreedyBatch(Batch):
    def __init__(self, moves: TransitionSystem, states, golds):
        self._moves = moves
        self._states = states
        self._next_states = [s for s in states if not s.is_final()]

    def advance(self, scores):
        self._next_states = self._moves.transition_states(self._next_states, scores)

    def advance_with_actions(self, actions):
        self._next_states = self._moves.apply_actions(self._next_states, actions)

    def get_states(self):
        return self._states

    @property
    def is_done(self):
        return all(s.is_final() for s in self._states)

    def get_unfinished_states(self):
        return [st for st in self._states if not st.is_final()]

    def __getitem__(self, i):
        return self._states[i]

    def __len__(self):
        return len(self._states)
