# cython: profile=True
from ._state cimport State
from ._state cimport at_eol, pop_stack, push_stack, add_dep
from ._state cimport has_head_in_buffer, has_child_in_buffer
from ._state cimport has_head_in_stack, has_child_in_stack
import index.hashes


cdef enum:
    ERR
    SHIFT
    REDUCE
    LEFT
    RIGHT
    N_MOVES


cdef inline bint _can_shift(const State* s) nogil:
    return not at_eol(s)


cdef inline bint _can_right(const State* s) nogil:
    return s.stack_len >= 1 and not at_eol(s)


cdef inline bint _can_left(const State* s) nogil:
    return s.stack_len >= 1 and s.heads[s.top] == 0


cdef inline bint _can_reduce(const State* s) nogil:
    return s.stack_len >= 2 and s.heads[s.top] != 0


cdef int _shift_cost(const State* s, list gold) except -1:
    assert not at_eol(s)
    cost = 0
    cost += has_head_in_stack(s, s.i, gold)
    cost += has_child_in_stack(s, s.i, gold)
    return cost


cdef int _right_cost(const State* s, list gold) except -1:
    assert s.stack_len >= 1
    cost = 0
    if gold[s.i] == s.top:
        return cost
    cost += has_head_in_buffer(s, s.i, gold)
    cost += has_child_in_stack(s, s.i, gold)
    cost += has_head_in_stack(s, s.i, gold)
    return cost


cdef int _left_cost(const State* s, list gold) except -1:
    assert s.stack_len >= 1
    cost = 0
    if gold[s.top] == s.i:
        return cost
    cost += has_head_in_buffer(s, s.top, gold)
    cost += has_child_in_buffer(s, s.top, gold)
    return cost


cdef int _reduce_cost(const State* s, list gold) except -1:
    assert s.stack_len >= 2
    cost = 0
    cost += has_child_in_buffer(s, s.top, gold)
    return cost


cdef class TransitionSystem:
    def __init__(self, list left_labels, list right_labels):
        self.mem = Pool()
        self.n_moves = 2 + len(left_labels) + len(right_labels) 
        moves = <Transition*>self.mem.alloc(self.n_moves, sizeof(Transition))
        cdef int i = 0
        moves[i].move = SHIFT
        moves[i].label = 0
        i += 1
        moves[i].move = REDUCE
        moves[i].label = 0
        i += 1
        cdef int label
        for label in left_labels:
            moves[i].move = LEFT
            moves[i].label = label
            i += 1
        for label in right_labels:
            moves[i].move = RIGHT
            moves[i].label = label
            i += 1
        self._moves = moves

    cdef int transition(self, State *s, const int clas) except -1:
        cdef const Transition* t = &self._moves[clas]
        if t.move == SHIFT:
            push_stack(s)
        elif t.move == LEFT:
            add_dep(s, s.i, s.top, t.label)
            pop_stack(s)
        elif t.move == RIGHT:
            add_dep(s, s.top, s.i, t.label)
            push_stack(s)
        elif t.move == REDUCE:
            pop_stack(s)
        else:
            raise StandardError(t.move)

    cdef int best_valid(self, const weight_t* scores, const State* s) except -1:
        cdef bint[N_MOVES] valid
        valid[SHIFT] = _can_shift(s)
        valid[LEFT] = _can_left(s)
        valid[RIGHT] = _can_right(s)
        valid[REDUCE] = _can_reduce(s)

        cdef int best = -1
        cdef weight_t score
        cdef int i
        for i in range(self.n_moves):
            if valid[self._moves[i].move] and scores[i] > score:
                best = i
                score = scores[i]
        assert best >= -1, "No valid moves found"
        return best

    cdef int best_gold(self, const weight_t* scores, const State* s,
                       list gold_heads, list gold_labels) except -1:
        cdef int[N_MOVES] unl_costs
        unl_costs[SHIFT] = _shift_cost(s, gold_heads) if _can_shift(s) else -1
        unl_costs[LEFT] = _left_cost(s, gold_heads) if _can_left(s) else -1
        unl_costs[RIGHT] = _right_cost(s, gold_heads) if _can_right(s) else -1
        unl_costs[REDUCE] = _reduce_cost(s, gold_heads) if _can_reduce(s) else -1

        cdef int cost
        cdef int label_cost
        cdef int move
        cdef int label
        cdef int best = -1
        cdef weight_t score
        cdef int i
        for i in range(self.n_moves):
            move = self._moves[i].move
            label = self._moves[i].label
            if unl_costs[move] == 0:
                if move == SHIFT or move == REDUCE:
                    label_cost = 0
                elif move == LEFT:
                    if gold_heads[s.top] == s.i:
                        label_cost = label != gold_labels[s.top]
                    else:
                        label_cost = 0
                elif move == RIGHT:
                    if gold_heads[s.i] == s.top:
                        label_cost = label != gold_labels[s.i]
                    else:
                        label_cost = 0
                else:
                    raise StandardError("Unknown Move")
                if label_cost == 0 and scores[i] > score:
                    best = i
                    score = scores[i]
        assert best >= -1, "No gold moves found"
        return best
