# cython: profile=True
from ._state cimport State
from ._state cimport has_head, get_idx, get_s0, get_n0
from ._state cimport is_final, at_eol, pop_stack, push_stack, add_dep
from ._state cimport head_in_buffer, children_in_buffer
from ._state cimport head_in_stack, children_in_stack

from ..tokens cimport TokenC


cdef enum:
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
    return s.stack_len >= 1 and not has_head(get_s0(s))


cdef inline bint _can_reduce(const State* s) nogil:
    return s.stack_len >= 2 and has_head(get_s0(s))


cdef int _shift_cost(const State* s, list gold) except -1:
    assert not at_eol(s)
    cost = 0
    cost += head_in_stack(s, s.i, gold)
    cost += children_in_stack(s, s.i, gold)
    return cost


cdef int _right_cost(const State* s, list gold) except -1:
    assert s.stack_len >= 1
    cost = 0
    if gold[s.i] == s.stack[0]:
        return cost
    cost += head_in_buffer(s, s.i, gold)
    cost += children_in_stack(s, s.i, gold)
    cost += head_in_stack(s, s.i, gold)
    return cost


cdef int _left_cost(const State* s, list gold) except -1:
    assert s.stack_len >= 1
    cost = 0
    if gold[s.stack[0]] == s.i:
        return cost

    cost += head_in_buffer(s, s.stack[0], gold)
    cost += children_in_buffer(s, s.stack[0], gold)
    return cost


cdef int _reduce_cost(const State* s, list gold) except -1:
    return children_in_buffer(s, s.stack[0], gold)


cdef class TransitionSystem:
    def __init__(self, list left_labels, list right_labels):
        self.mem = Pool()
        if 'ROOT' in right_labels:
            right_labels.pop(right_labels.index('ROOT'))
        if 'ROOT' in left_labels:
            left_labels.pop(left_labels.index('ROOT'))
        self.n_moves = 2 + len(left_labels) + len(right_labels) 
        moves = <Transition*>self.mem.alloc(self.n_moves, sizeof(Transition))
        cdef int i = 0
        moves[i].move = SHIFT
        moves[i].label = 0
        i += 1
        moves[i].move = REDUCE
        moves[i].label = 0
        i += 1
        self.label_ids = {'ROOT': 0}
        cdef int label_id
        for label_str in left_labels:
            label_id = self.label_ids.setdefault(label_str, len(self.label_ids))
            moves[i].move = LEFT
            moves[i].label = label_id
            i += 1
        for label_str in right_labels:
            label_id = self.label_ids.setdefault(label_str, len(self.label_ids))
            moves[i].move = RIGHT
            moves[i].label = label_id
            i += 1
        self._moves = moves

    cdef int transition(self, State *s, const int clas) except -1:
        cdef const Transition* t = &self._moves[clas]
        if t.move == SHIFT:
            push_stack(s)
        elif t.move == LEFT:
            add_dep(s, s.i, s.stack[0], t.label)
            pop_stack(s)
        elif t.move == RIGHT:
            add_dep(s, s.stack[0], s.i, t.label)
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
        cdef weight_t score = -90000
        cdef int i
        for i in range(self.n_moves):
            if valid[self._moves[i].move] and scores[i] > score:
                best = i
                score = scores[i]
        return best

    cdef int best_gold(self, const weight_t* scores, const State* s,
                       list gold_heads, list label_strings) except -1:
        gold_labels = [self.label_ids[label_str] for label_str in label_strings]
        cdef int[N_MOVES] unl_costs
        unl_costs[SHIFT] = _shift_cost(s, gold_heads) if _can_shift(s) else -1
        unl_costs[LEFT] = _left_cost(s, gold_heads) if _can_left(s) else -1
        unl_costs[RIGHT] = _right_cost(s, gold_heads) if _can_right(s) else -1
        unl_costs[REDUCE] = _reduce_cost(s, gold_heads) if _can_reduce(s) else -1

        cdef int cost
        cdef int move
        cdef int label
        cdef int best = -1
        cdef weight_t score = -9000
        cdef int i
        for i in range(self.n_moves):
            move = self._moves[i].move
            label = self._moves[i].label
            if unl_costs[move] == 0:
                if move == SHIFT or move == REDUCE:
                    cost = 0
                elif move == LEFT:
                    if gold_heads[s.stack[0]] == s.i:
                        cost = label != gold_labels[s.stack[0]]
                    else:
                        cost = 0
                elif move == RIGHT:
                    if gold_heads[s.i] == s.stack[0]:
                        cost = label != gold_labels[s.i]
                    else:
                        cost = 0
                else:
                    raise StandardError("Unknown Move")
                if cost == 0 and (best == -1 or scores[i] > score):
                    best = i
                    score = scores[i]
 
        if best < 0:
            print unl_costs[SHIFT], unl_costs[REDUCE], unl_costs[LEFT], unl_costs[RIGHT]
            print s.stack_len
            print has_head(get_s0(s))
            print s.sent[s.stack[0]].head
            print s.stack[0], s.i
            print gold_heads[s.stack[0]], gold_heads[s.i]
            print gold_labels[s.i]
            print children_in_buffer(s, s.stack[0], gold_heads)
            print head_in_buffer(s, s.stack[0], gold_heads)
            raise StandardError 
        return best
