from __future__ import unicode_literals

from ._state cimport begin_entity
from ._state cimport end_entity
from ._state cimport entity_is_open
from ._state cimport entity_is_sunk


ACTION_NAMES = ['' for _ in range(N_ACTIONS)]
ACTION_NAMES[<int>BEGIN] = 'B'
ACTION_NAMES[<int>IN] = 'I'
ACTION_NAMES[<int>LAST] = 'L'
ACTION_NAMES[<int>UNIT] = 'U'
ACTION_NAMES[<int>OUT] = 'O'


cdef bint can_begin(State* s, int label):
    return not entity_is_open(s)


cdef bint can_in(State* s, int label):
    return entity_is_open(s) and s.curr.label == label


cdef bint can_last(State* s, int label):
    return entity_is_open(s) and s.curr.label == label


cdef bint can_unit(State* s, int label):
    return not entity_is_open(s)


cdef bint can_out(State* s, int label):
    return not entity_is_open(s)


cdef bint is_oracle(ActionType act, int tag, ActionType g_act, int g_tag,
                    ActionType next_act, bint is_sunk):
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
            return is_sunk and next_act == OUT
        elif g_act == OUT:
            # I, Gold O --> True iff next tag == O
            return next_act == OUT
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
    

cdef int set_accept_if_valid(Move* moves, int n_classes, State* s) except 0:
    cdef int n_accept = 0
    cdef Move* m
    for i in range(n_classes):
        m = &moves[i]
        if m.action == BEGIN:
            m.accept = can_begin(s, m.label)
        elif m.action == IN:
            m.accept = can_in(s, m.label)
        elif m.action == LAST:
            m.accept = can_last(s, m.label)
        elif m.action == UNIT:
            m.accept = can_unit(s, m.label)
        elif m.action == OUT:
            m.accept = can_out(s, m.label)
        n_accept += m.accept
    assert n_accept != 0
    return n_accept


cdef int set_accept_if_oracle(Move* moves, Move* golds, int n_classes, State* s) except 0:

    cdef Move* g = &golds[s.i]
    cdef ActionType next_act = <ActionType>golds[s.i+1].action if s.i < s.length else OUT
    cdef bint is_sunk = entity_is_sunk(s, golds)
    cdef Move* m
    cdef int n_accept = 0
    set_accept_if_valid(moves, n_classes, s)
    for i in range(n_classes):
        m = &moves[i]
        if not m.accept:
            continue
        m.accept = is_oracle(<ActionType>m.action, m.label, <ActionType>g.action,
                             g.label, next_act, is_sunk)
        n_accept += m.accept
    assert n_accept != 0
    return n_accept


cdef Move* best_accepted(Move* moves, weight_t* scores, int n) except NULL:
    cdef int first_accept
    for first_accept in range(n):
        if moves[first_accept].accept:
            break
    else:
        raise StandardError
    cdef int best = first_accept
    cdef weight_t score = scores[first_accept]
    cdef int i
    for i in range(first_accept+1, n): 
        if moves[i].accept and scores[i] > score:
            best = i
            score = scores[i]
    return &moves[best]


cdef int transition(State *s, Move* move) except -1:
    if move.action == BEGIN:
        begin_entity(s, move.label)
    elif move.action == IN:
        pass
    elif move.action == LAST:
        end_entity(s)
    elif move.action == UNIT:
        begin_entity(s, move.label)
        end_entity(s)
    elif move.action == OUT:
        pass
    s.tags[s.i] = move.clas 
    s.i += 1


def get_n_moves(n_tags):
    return n_tags + n_tags + n_tags + n_tags + 1


cdef int fill_moves(Move* moves, int n_tags) except -1:
    cdef int i = 0
    for label in range(n_tags):
        moves[i].action = BEGIN
        moves[i].label = label
        i += 1
    for label in range(n_tags):
        moves[i].action = IN
        moves[i].label = label
        i += 1
    for label in range(n_tags):
        moves[i].action = LAST
        moves[i].label = label
        i += 1
    for label in range(n_tags):
        moves[i].action = UNIT
        moves[i].label = label
        i += 1
    moves[i].action = OUT
    moves[i].label = 0
