from __future__ import unicode_literals

from ._state cimport State
from ._state cimport has_head, get_idx, get_s0, get_n0
from ._state cimport is_final, at_eol, pop_stack, push_stack, add_dep
from ._state cimport head_in_buffer, children_in_buffer
from ._state cimport head_in_stack, children_in_stack

from ..structs cimport TokenC

from .transition_system cimport do_func_t, get_cost_func_t
from .conll cimport GoldParse


DEF NON_MONOTONIC = True
DEF USE_BREAK = True

cdef weight_t MIN_SCORE = -90000

# Break transition from here
# http://www.aclweb.org/anthology/P13-1074
cdef enum:
    SHIFT
    REDUCE
    LEFT
    RIGHT
    BREAK
    N_MOVES


cdef do_func_t[N_MOVES] do_funcs
cdef get_cost_func_t[N_MOVES] get_cost_funcs


cdef class ArcEager(TransitionSystem):
    @classmethod
    def get_labels(cls, gold_parses):
        labels = {RIGHT: {}, LEFT: {}}
        for parse in gold_parses:
            for i, (head, label) in enumerate(zip(parse.heads, parse.labels)):
                if head > i:
                    labels[RIGHT][label] = True
                else:
                    labels[LEFT][label] = True
        return labels

    cdef Transition init_transition(self, int clas, int move, int label) except *:
        # TODO: Apparent Cython bug here when we try to use the Transition()
        # constructor with the function pointers
        cdef Transition t
        t.score = 0
        t.clas = clas
        t.move = move
        t.label = label
        t.do = do_funcs[move]
        t.get_cost = get_cost_funcs[move]
        return t

    cdef Transition best_valid(self, const weight_t* scores, const State* s) except *:
        cdef bint[N_MOVES] is_valid
        is_valid[SHIFT] = _can_shift(s)
        is_valid[REDUCE] = _can_reduce(s)
        is_valid[LEFT] = _can_left(s)
        is_valid[RIGHT] = _can_right(s)
        is_valid[BREAK] = _can_break(s)
        cdef Transition best
        cdef weight_t score = MIN_SCORE
        cdef int i
        for i in range(self.n_moves):
            if scores[i] > score and is_valid[self.c[i].move]:
                best = self.c[i]
                score = scores[i]
        # Label Shift moves with the best Right-Arc label, for non-monotonic
        # actions
        if best.move == SHIFT:
            score = MIN_SCORE
            for i in range(self.n_moves):
                if self.c[i].move == RIGHT and scores[i] > score:
                    best.label = self.c[i].label
                    score = scores[i]
        return best


cdef int _do_shift(const Transition* self, State* state) except -1:
    # Set the dep label, in case we need it after we reduce
    if NON_MONOTONIC:
        get_s0(state).dep = self.label
    push_stack(state)


cdef int _do_left(const Transition* self, State* state) except -1:
    add_dep(state, state.i, state.stack[0], self.label)
    pop_stack(state)


cdef int _do_right(const Transition* self, State* state) except -1:
    add_dep(state, state.stack[0], state.i, self.label)
    push_stack(state)


cdef int _do_reduce(const Transition* self, State* state) except -1:
    # TODO: Huh? Is this some weirdness from the non-monotonic?
    add_dep(state, state.stack[-1], state.stack[0], get_s0(state).dep)
    pop_stack(state)


cdef int _do_break(const Transition* self, State* state) except -1:
    state.sent[state.i-1].sent_end = True
    while state.stack_len != 0:
        if get_s0(state).head == 0:
            get_s0(state).dep = 0
        state.stack -= 1
        state.stack_len -= 1
    if not at_eol(state):
        push_stack(state)


do_funcs[SHIFT] = _do_shift
do_funcs[REDUCE] = _do_reduce
do_funcs[LEFT] = _do_left
do_funcs[RIGHT] = _do_right
do_funcs[BREAK] = _do_break


cdef int _shift_cost(const Transition* self, const State* s, GoldParse gold) except -1:
    assert not at_eol(s)
    cost = 0
    cost += head_in_stack(s, s.i, gold.c_heads)
    cost += children_in_stack(s, s.i, gold.c_heads)
    if NON_MONOTONIC:
        cost += gold[s.stack[0]] == s.i
    # If we can break, and there's no cost to doing so, we should
    if _can_break(s) and _break_cost(self, s, gold) == 0:
        cost += 1
    return cost


cdef int _right_cost(const Transition* self, const State* s, GoldParse gold) except -1:
    assert s.stack_len >= 1
    cost = 0
    if gold[s.i] == s.stack[0]:
        return cost
    cost += head_in_buffer(s, s.i, gold.c_heads)
    cost += children_in_stack(s, s.i, gold.c_heads)
    cost += head_in_stack(s, s.i, gold.c_heads)
    if NON_MONOTONIC:
        cost += gold[s.stack[0]] == s.i
    return cost


cdef int _left_cost(const Transition* self, const State* s, GoldParse gold) except -1:
    assert s.stack_len >= 1
    cost = 0
    if gold[s.stack[0]] == s.i:
        return cost

    cost += head_in_buffer(s, s.stack[0], gold.c_heads)
    cost += children_in_buffer(s, s.stack[0], gold.c_heads)
    if NON_MONOTONIC and s.stack_len >= 2:
        cost += gold[s.stack[0]] == s.stack[-1]
    cost += gold[s.stack[0]] == s.stack[0]
    return cost


cdef int _reduce_cost(const Transition* self, const State* s, GoldParse gold) except -1:
    cdef int cost = 0
    cost += children_in_buffer(s, s.stack[0], gold.c_heads)
    if NON_MONOTONIC:
        cost += head_in_buffer(s, s.stack[0], gold.c_heads)
    return cost


cdef int _break_cost(const Transition* self, const State* s, GoldParse gold) except -1:
    # When we break, we Reduce all of the words on the stack.
    cdef int cost = 0
    # Number of deps between S0...Sn and N0...Nn
    for i in range(s.i, s.sent_len):
        cost += children_in_stack(s, i, gold.c_heads)
        cost += head_in_stack(s, i, gold.c_heads)
    return cost


get_cost_funcs[SHIFT] = _shift_cost
get_cost_funcs[REDUCE] = _reduce_cost
get_cost_funcs[LEFT] = _left_cost
get_cost_funcs[RIGHT] = _right_cost
get_cost_funcs[BREAK] = _break_cost


cdef inline bint _can_shift(const State* s) nogil:
    return not at_eol(s)


cdef inline bint _can_right(const State* s) nogil:
    return s.stack_len >= 1 and not at_eol(s)


cdef inline bint _can_left(const State* s) nogil:
    if NON_MONOTONIC:
        return s.stack_len >= 1
    else:
        return s.stack_len >= 1 and not has_head(get_s0(s))


cdef inline bint _can_reduce(const State* s) nogil:
    if NON_MONOTONIC:
        return s.stack_len >= 2
    else:
        return s.stack_len >= 2 and has_head(get_s0(s))


cdef inline bint _can_break(const State* s) nogil:
    cdef int i
    if not USE_BREAK:
        return False
    elif at_eol(s):
        return False
    else:
        # If stack is disconnected, cannot break
        seen_headless = False
        for i in range(s.stack_len):
            if s.sent[s.stack[-i]].head == 0:
                if seen_headless:
                    return False
                else:
                    seen_headless = True
        return True
