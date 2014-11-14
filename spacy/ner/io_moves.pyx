from __future__ import unicode_literals
from cymem.cymem cimport Pool

from thinc.typedefs cimport class_t
from thinc.typedefs cimport weight_t

from ._state cimport begin_entity
from ._state cimport end_entity
from ._state cimport entity_is_open


ACTION_NAMES = ['' for _ in range(N_ACTIONS)]
ACTION_NAMES[<int>MISSING] = '?'
ACTION_NAMES[<int>SHIFT] = 'S'
ACTION_NAMES[<int>REDUCE] = 'R'
ACTION_NAMES[<int>OUT] = 'O'


cdef int set_accept_if_oracle(Move* moves, int n, State* s,
                              int* g_starts, int* g_ends, int* g_labels) except 0:
    # If curr entity: (O invalid)
    #   if cost is not sunk (start matches, end is i-1 or greater
    #     - If i-1 == gold.end --> R=True, S=False
    #     - Shift if end >= i --> S=True, R=False
    #   else
    #     - If i == gold.start --> R=True, S=False
    #     - Else --> R=True, S=True
    # Else (R invalid):
    #   if start == gold.start: S=True, O=False
    #   else: O=True, S=False
    if entity_is_open(s):
        g_start = g_starts[s.curr.start]
        g_end = g_ends[s.curr.start]
        accept_o = False
        if g_start == s.curr.start and g_end == s.i:
            accept_r = True
            accept_s = False
        elif g_start == s.curr.start and g_end > s.i:
            accept_s = True
            s_label = s.curr.label
            accept_r = False
        elif g_starts[s.i] == s.i:
            accept_r = True
            accept_s = False
        else:
            accept_r = True
            accept_s = True
            s_label = s.curr.label
    else:
        accept_r = False
        if g_starts[s.i] == s.i:
            accept_s = True
            s_label = g_labels[s.i]
            accept_o = False
        else:
            accept_o = True
            accept_s = False
    n_accept = 0
    moves[0].accept = False
    for i in range(1, n):
        m = &moves[i]
        if m.action == SHIFT:
            m.accept = accept_s and m.label == s_label
        elif m.action == REDUCE:
            m.accept = accept_r
        elif m.action == OUT:
            m.accept = accept_o
        n_accept += m.accept
    assert n_accept != 0
    return n_accept


cdef int set_accept_if_valid(Move* moves, int n, State* s) except 0:
    cdef int i
    cdef bint open_ent = entity_is_open(s)
    cdef int n_accept = 0
    moves[0].accept = False
    for i in range(1, n):
        if moves[i].action == SHIFT:
            if s.i >= s.length:
                moves[i].accept = False
            elif open_ent and moves[i].label != s.curr.label:
                moves[i].accept = False
            else:
                moves[i].accept = True
        elif moves[i].action == REDUCE:
            moves[i].accept = open_ent
        elif moves[i].action == OUT:
            moves[i].accept = s.i < s.length and not open_ent
        n_accept += moves[i].accept
    return n_accept


cdef Move* best_accepted(Move* moves, weight_t* scores, int n) except NULL:
    cdef int first_accept = -1
    for first_accept in range(1, n):
        if moves[first_accept].accept:
            break
    else:
        raise StandardError
    assert first_accept != -1
    cdef int best = first_accept
    cdef weight_t score = scores[first_accept-1]
    cdef int i
    for i in range(first_accept+1, n): 
        if moves[i].accept and scores[i-1] > score:
            best = i
            score = scores[i-1]
    return &moves[best]


cdef int transition(State *s, Move* move) except -1:
    s.tags[s.i] = move.clas 
    if move.action == OUT:
        s.i += 1
    elif move.action == SHIFT:
        if not entity_is_open(s):
            s.curr.start = s.i
            s.curr.label = move.label
        s.i += 1
    elif move.action == REDUCE:
        s.curr.end = s.i
        s.ents[s.j] = s.curr
        s.j += 1
        s.curr.start = 0
        s.curr.label = -1
        s.curr.end = 0
    else:
        raise ValueError(move.action)


def get_n_moves(n_tags):
    return 1 + 1 + 1 + n_tags


cdef int fill_moves(Move* moves, int n, list entity_types) except -1:
    cdef Move* m
    label_names = {'-': 0}
    # Reserve class 0
    cdef int i = 0
    moves[i].clas = i
    moves[i].action = MISSING
    moves[i].label = 0
    i += 1
    for entity_type in entity_types:
        moves[i].action = SHIFT
        moves[i].label = label_names.setdefault(entity_type, len(label_names))
        moves[i].clas = i
        i += 1
    moves[i].clas = i
    moves[i].action = OUT
    moves[i].label = 0
    i += 1
    moves[i].action = REDUCE
    moves[i].clas = i
    moves[i].label = 0
    i += 1


cdef bint is_final(State* s):
    return s.i == s.length and not entity_is_open(s)
