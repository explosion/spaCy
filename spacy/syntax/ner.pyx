from __future__ import unicode_literals

from ._state cimport State
from ._state cimport has_head, get_idx, get_s0, get_n0
from ._state cimport is_final, at_eol, pop_stack, push_stack, add_dep
from ._state cimport head_in_buffer, children_in_buffer
from ._state cimport head_in_stack, children_in_stack

from ..structs cimport TokenC


DEF NON_MONOTONIC = True
DEF USE_BREAK = True


cdef enum:
    MISSING
    BEGIN
    IN
    LAST
    UNIT
    OUT
    N_MOVES


cdef int is_valid(ActionType act, int label, State* s) except -1:
    if act == BEGIN:
        return not entity_is_open(s)
    elif act == IN:
        return entity_is_open(s) and s.curr.label == label
    elif act == LAST:
        return entity_is_open(s) and s.curr.label == label
    elif act == UNIT:
        return not entity_is_open(s)
    elif act == OUT:
        return not entity_is_open(s)
    else:
        raise UnknownMove(act, label)


cdef bint is_gold(ActionType act, int tag, ActionType g_act, int g_tag,
                 ActionType next_act, bint is_sunk):
    if g_act == MISSING:
        return True
    if act == BEGIN:
        if g_act == BEGIN:
            # B, Gold B --> Label match
            return tag == g_tag
        else:
            # B, Gold I --> False (P)
            # B, Gold L --> False (P)
            # B, Gold O --> False (P)
            # B, Gold U --> False (P)
            return False
    elif act == IN:
        if g_act == BEGIN:
            # I, Gold B --> True (P of bad open entity sunk, R of this entity sunk)
            return True
        elif g_act == IN:
            # I, Gold I --> True (label forced by prev, if mismatch, P and R both sunk)
            return True
        elif g_act == LAST:
            # I, Gold L --> True iff this entity sunk and next tag == O
            return is_sunk and (next_act == OUT or next_act == MISSING)
        elif g_act == OUT:
            # I, Gold O --> True iff next tag == O
            return next_act == OUT or next_act == MISSING
        elif g_act == UNIT:
            # I, Gold U --> True iff next tag == O
            return next_act == OUT
    elif act == LAST:
        if g_act == BEGIN:
            # L, Gold B --> True
            return True
        elif g_act == IN:
            # L, Gold I --> True iff this entity sunk
            return is_sunk
        elif g_act == LAST:
            # L, Gold L --> True
            return True
        elif g_act == OUT:
            # L, Gold O --> True
            return True
        elif g_act == UNIT:
            # L, Gold U --> True
            return True
    elif act == OUT:
        if g_act == BEGIN:
            # O, Gold B --> False
            return False
        elif g_act == IN:
            # O, Gold I --> True
            return True
        elif g_act == LAST:
            # O, Gold L --> True
            return True
        elif g_act == OUT:
            # O, Gold O --> True
            return True
        elif g_act == UNIT:
            # O, Gold U --> False
            return False
    elif act == UNIT:
        if g_act == UNIT:
            # U, Gold U --> True iff tag match
            return tag == g_tag
        else:
            # U, Gold B --> False
            # U, Gold I --> False
            # U, Gold L --> False
            # U, Gold O --> False
            return False


cdef bint entity_is_open(State *s) except -1:
    return s.sent[s.i - 1].ent.tag >= 1


cdef bint entity_is_sunk(State *s, Move* golds) except -1:
    if not entity_is_open(s):
        return False

    cdef const Entity* curr = &s.sent[s.i - 1].ent
    cdef Move* gold = &golds[(s.i - 1) + curr.start]
    if gold.action != BEGIN and gold.action != UNIT:
        return True
    elif gold.label != s.curr.label:
        return True
    else:
        return False


cdef class TransitionSystem:
    def __init__(self, list entity_type_strs):
        self.mem = Pool()

        cdef Move* m
        label_names = {'-': 0}
        for i, tag_name in enumerate(tag_names):
            m = &moves[i]
            if '-' in tag_name:
                action_str, label = tag_name.split('-')
            elif tag_name == 'O':
                action_str = 'O'
                label = '-'
            elif tag_name == 'NULL' or tag_name == 'EOL':
                action_str = '?'
                label = '-'
            else:
                raise StandardError(tag_name)
            m.action = ACTION_NAMES.index(action_str)
            m.label = label_names.setdefault(label, len(label_names))
            m.clas = i

    cdef int transition(self, State *s, Move* move) except -1:
        if move.action == BEGIN:
            s.curr.start = s.i
            s.curr.label = label
        elif move.action == IN:
            pass
        elif move.action == LAST:
            s.curr.end = s.i
            s.ents[s.j] = s.curr
            s.j += 1
            s.curr.start = 0
            s.curr.label = -1
            s.curr.end = 0
        elif move.action == UNIT:
            begin_entity(s, move.label)
            end_entity(s)
        elif move.action == OUT:
            pass
        s.tags[s.i] = move.clas 
        s.i += 1

    cdef Transition best_valid(self, const weight_t* scores, const State* s) except *:
        cdef int best = -1
        cdef weight_t score = -90000
        cdef const Transition* m
        cdef int i
        for i in range(self.n_moves):
            m = &self._moves[i]
            if _is_valid(s, m.ent_move, m.ent_label) and scores[i] > score:
                best = i
                score = scores[i]
        assert best >= 0
        cdef Transition t = self._moves[best]
        t.score = score
        return t

    cdef Transition best_gold(self, Transition* guess, const weight_t* scores,
                              const State* s, Move* golds) except *:

        cdef Move* g = &golds[s.i]
        cdef ActionType next_act = <ActionType>golds[s.i+1].action if s.i < s.length else OUT
        cdef bint is_sunk = entity_is_sunk(s, golds)
        cdef Move* m
        cdef int n_accept = 0
        for i in range(1, self.n_classes):
            m = &moves[i]
            if _is_valid(s, m.move, m.label) and \
               _is_gold(s, m.move, m.label, next_act, is_sunk) and \
               scores[i] > score:
                best = i
                score = scores[i]
    assert best >= 0
    return self._moves[best]


class OracleError(Exception):
    pass


class UnknownMove(Exception):
    pass
