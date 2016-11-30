from __future__ import unicode_literals

import ctypes
import os

from ..structs cimport TokenC

from .transition_system cimport do_func_t, get_cost_func_t
from .transition_system cimport move_cost_func_t, label_cost_func_t
from ..gold cimport GoldParse
from ..gold cimport GoldParseC
from ..attrs cimport TAG, HEAD, DEP, ENT_IOB, ENT_TYPE, IS_SPACE
from ..lexeme cimport Lexeme

from libc.stdint cimport uint32_t
from libc.string cimport memcpy

from cymem.cymem cimport Pool
from .stateclass cimport StateClass
from ._state cimport StateC, is_space_token
from .nonproj import PseudoProjectivity
from .nonproj import is_nonproj_tree


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


MOVE_NAMES = [None] * N_MOVES
MOVE_NAMES[SHIFT] = 'S'
MOVE_NAMES[REDUCE] = 'D'
MOVE_NAMES[LEFT] = 'L'
MOVE_NAMES[RIGHT] = 'R'
MOVE_NAMES[BREAK] = 'B'


# Helper functions for the arc-eager oracle

cdef weight_t push_cost(StateClass stcls, const GoldParseC* gold, int target) nogil:
    cdef weight_t cost = 0
    cdef int i, S_i
    for i in range(stcls.stack_depth()):
        S_i = stcls.S(i)
        if gold.heads[target] == S_i:
            cost += 1
        if gold.heads[S_i] == target and (NON_MONOTONIC or not stcls.has_head(S_i)):
            cost += 1
    cost += Break.is_valid(stcls.c, -1) and Break.move_cost(stcls, gold) == 0
    return cost


cdef weight_t pop_cost(StateClass stcls, const GoldParseC* gold, int target) nogil:
    cdef weight_t cost = 0
    cdef int i, B_i
    for i in range(stcls.buffer_length()):
        B_i = stcls.B(i)
        cost += gold.heads[B_i] == target
        cost += gold.heads[target] == B_i
        if gold.heads[B_i] == B_i or gold.heads[B_i] < target:
            break
    if Break.is_valid(stcls.c, -1) and Break.move_cost(stcls, gold) == 0:
        cost += 1
    return cost


cdef weight_t arc_cost(StateClass stcls, const GoldParseC* gold, int head, int child) nogil:
    if arc_is_gold(gold, head, child):
        return 0
    elif stcls.H(child) == gold.heads[child]:
        return 1
    # Head in buffer
    elif gold.heads[child] >= stcls.B(0) and stcls.B(1) != -1:
        return 1
    else:
        return 0


cdef bint arc_is_gold(const GoldParseC* gold, int head, int child) nogil:
    if gold.labels[child] == -1:
        return True
    elif gold.heads[child] == head:
        return True
    else:
        return False


cdef bint label_is_gold(const GoldParseC* gold, int head, int child, int label) nogil:
    if gold.labels[child] == -1:
        return True
    elif label == -1:
        return True
    elif gold.labels[child] == label:
        return True
    else:
        return False


cdef bint _is_gold_root(const GoldParseC* gold, int word) nogil:
    return gold.labels[word] == -1 or gold.heads[word] == word


cdef class Shift:
    @staticmethod
    cdef bint is_valid(const StateC* st, int label) nogil:
        return st.buffer_length() >= 2 and not st.shifted[st.B(0)] and not st.B_(0).sent_start

    @staticmethod
    cdef int transition(StateC* st, int label) nogil:
        st.push()
        st.fast_forward()

    @staticmethod
    cdef weight_t cost(StateClass st, const GoldParseC* gold, int label) nogil:
        return Shift.move_cost(st, gold) + Shift.label_cost(st, gold, label)

    @staticmethod
    cdef inline weight_t move_cost(StateClass s, const GoldParseC* gold) nogil:
        return push_cost(s, gold, s.B(0))

    @staticmethod
    cdef inline weight_t label_cost(StateClass s, const GoldParseC* gold, int label) nogil:
        return 0


cdef class Reduce:
    @staticmethod
    cdef bint is_valid(const StateC* st, int label) nogil:
        return st.stack_depth() >= 2

    @staticmethod
    cdef int transition(StateC* st, int label) nogil:
        if st.has_head(st.S(0)):
            st.pop()
        else:
            st.unshift()
        st.fast_forward()

    @staticmethod
    cdef weight_t cost(StateClass s, const GoldParseC* gold, int label) nogil:
        return Reduce.move_cost(s, gold) + Reduce.label_cost(s, gold, label)

    @staticmethod
    cdef inline weight_t move_cost(StateClass st, const GoldParseC* gold) nogil:
        return pop_cost(st, gold, st.S(0))

    @staticmethod
    cdef inline weight_t label_cost(StateClass s, const GoldParseC* gold, int label) nogil:
        return 0


cdef class LeftArc:
    @staticmethod
    cdef bint is_valid(const StateC* st, int label) nogil:
        return not st.B_(0).sent_start

    @staticmethod
    cdef int transition(StateC* st, int label) nogil:
        st.add_arc(st.B(0), st.S(0), label)
        st.pop()
        st.fast_forward()

    @staticmethod
    cdef weight_t cost(StateClass s, const GoldParseC* gold, int label) nogil:
        return LeftArc.move_cost(s, gold) + LeftArc.label_cost(s, gold, label)

    @staticmethod
    cdef inline weight_t move_cost(StateClass s, const GoldParseC* gold) nogil:
        cdef weight_t cost = 0
        if arc_is_gold(gold, s.B(0), s.S(0)):
            return 0
        else:
            # Account for deps we might lose between S0 and stack
            if not s.has_head(s.S(0)):
                for i in range(1, s.stack_depth()):
                    cost += gold.heads[s.S(i)] == s.S(0)
                    cost += gold.heads[s.S(0)] == s.S(i)
            return cost + pop_cost(s, gold, s.S(0)) + arc_cost(s, gold, s.B(0), s.S(0))

    @staticmethod
    cdef inline weight_t label_cost(StateClass s, const GoldParseC* gold, int label) nogil:
        return arc_is_gold(gold, s.B(0), s.S(0)) and not label_is_gold(gold, s.B(0), s.S(0), label)


cdef class RightArc:
    @staticmethod
    cdef bint is_valid(const StateC* st, int label) nogil:
        return not st.B_(0).sent_start

    @staticmethod
    cdef int transition(StateC* st, int label) nogil:
        st.add_arc(st.S(0), st.B(0), label)
        st.push()
        st.fast_forward()

    @staticmethod
    cdef inline weight_t cost(StateClass s, const GoldParseC* gold, int label) nogil:
        return RightArc.move_cost(s, gold) + RightArc.label_cost(s, gold, label)

    @staticmethod
    cdef inline weight_t move_cost(StateClass s, const GoldParseC* gold) nogil:
        if arc_is_gold(gold, s.S(0), s.B(0)):
            return 0
        elif s.c.shifted[s.B(0)]:
            return push_cost(s, gold, s.B(0))
        else:
            return push_cost(s, gold, s.B(0)) + arc_cost(s, gold, s.S(0), s.B(0))

    @staticmethod
    cdef weight_t label_cost(StateClass s, const GoldParseC* gold, int label) nogil:
        return arc_is_gold(gold, s.S(0), s.B(0)) and not label_is_gold(gold, s.S(0), s.B(0), label)


cdef class Break:
    @staticmethod
    cdef bint is_valid(const StateC* st, int label) nogil:
        cdef int i
        if not USE_BREAK:
            return False
        elif st.at_break():
            return False
        elif st.stack_depth() < 1:
            return False
        else:
            return True

    @staticmethod
    cdef int transition(StateC* st, int label) nogil:
        st.set_break(st.B_(0).l_edge)
        st.fast_forward()

    @staticmethod
    cdef weight_t cost(StateClass s, const GoldParseC* gold, int label) nogil:
        return Break.move_cost(s, gold) + Break.label_cost(s, gold, label)

    @staticmethod
    cdef inline weight_t move_cost(StateClass s, const GoldParseC* gold) nogil:
        cdef weight_t cost = 0
        cdef int i, j, S_i, B_i
        for i in range(s.stack_depth()):
            S_i = s.S(i)
            for j in range(s.buffer_length()):
                B_i = s.B(j)
                cost += gold.heads[S_i] == B_i
                cost += gold.heads[B_i] == S_i
        # Check for sentence boundary --- if it's here, we can't have any deps
        # between stack and buffer, so rest of action is irrelevant.
        s0_root = _get_root(s.S(0), gold)
        b0_root = _get_root(s.B(0), gold)
        if s0_root != b0_root or s0_root == -1 or b0_root == -1:
            return cost
        else:
            return cost + 1

    @staticmethod
    cdef inline weight_t label_cost(StateClass s, const GoldParseC* gold, int label) nogil:
        return 0

cdef int _get_root(int word, const GoldParseC* gold) nogil:
    while gold.heads[word] != word and gold.labels[word] != -1 and word >= 0:
        word = gold.heads[word]
    if gold.labels[word] == -1:
        return -1
    else:
        return word


cdef class ArcEager(TransitionSystem):
    @classmethod
    def get_actions(cls, **kwargs):
        actions = kwargs.get('actions', 
                    {
                        SHIFT: {'': True},
                        REDUCE: {'': True},
                        RIGHT: {},
                        LEFT: {},
                        BREAK: {'ROOT': True}})
        for label in kwargs.get('left_labels', []):
            if label.upper() != 'ROOT':
                actions[LEFT][label] = True
        for label in kwargs.get('right_labels', []):
            if label.upper() != 'ROOT':
                actions[RIGHT][label] = True
 
        for raw_text, sents in kwargs.get('gold_parses', []):
            for (ids, words, tags, heads, labels, iob), ctnts in sents:
                for child, head, label in zip(ids, heads, labels):
                    if label.upper() == 'ROOT':
                        label = 'ROOT'
                    if label != 'ROOT':
                        if head < child:
                            actions[RIGHT][label] = True
                        elif head > child:
                            actions[LEFT][label] = True
        return actions

    property action_types:
        def __get__(self):
            return (SHIFT, REDUCE, LEFT, RIGHT, BREAK)

    cdef int preprocess_gold(self, GoldParse gold) except -1:
        for i in range(gold.length):
            if gold.heads[i] is None: # Missing values
                gold.c.heads[i] = i
                gold.c.labels[i] = -1
            else:
                label = gold.labels[i]
                if label.upper() == 'ROOT':
                    label = 'ROOT'
                gold.c.heads[i] = gold.heads[i]
                gold.c.labels[i] = self.strings[label]
                # Count frequencies, for use in encoder
                self.freqs[HEAD][gold.c.heads[i] - i] += 1
                self.freqs[DEP][gold.c.labels[i]] += 1

    cdef Transition lookup_transition(self, object name) except *:
        if '-' in name:
            move_str, label_str = name.split('-', 1)
            label = self.strings[label_str]
        else:
            move_str = name
            label = 0
        move = MOVE_NAMES.index(move_str)
        for i in range(self.n_moves):
            if self.c[i].move == move and self.c[i].label == label:
                return self.c[i]

    def move_name(self, int move, int label):
        label_str = self.strings[label]
        if label_str:
            return MOVE_NAMES[move] + '-' + label_str
        else:
            return MOVE_NAMES[move]

    cdef Transition init_transition(self, int clas, int move, int label) except *:
        # TODO: Apparent Cython bug here when we try to use the Transition()
        # constructor with the function pointers
        cdef Transition t
        t.score = 0
        t.clas = clas
        t.move = move
        t.label = label
        if move == SHIFT:
            t.is_valid = Shift.is_valid
            t.do = Shift.transition
            t.get_cost = Shift.cost
        elif move == REDUCE:
            t.is_valid = Reduce.is_valid
            t.do = Reduce.transition
            t.get_cost = Reduce.cost
        elif move == LEFT:
            t.is_valid = LeftArc.is_valid
            t.do = LeftArc.transition
            t.get_cost = LeftArc.cost
        elif move == RIGHT:
            t.is_valid = RightArc.is_valid
            t.do = RightArc.transition
            t.get_cost = RightArc.cost
        elif move == BREAK:
            t.is_valid = Break.is_valid
            t.do = Break.transition
            t.get_cost = Break.cost
        else:
            raise Exception(move)
        return t

    cdef int initialize_state(self, StateC* st) nogil:
        # Ensure sent_start is set to 0 throughout
        for i in range(st.length):
            st._sent[i].sent_start = False
            st._sent[i].l_edge = i
            st._sent[i].r_edge = i
        st.fast_forward()

    cdef int finalize_state(self, StateC* st) nogil:
        cdef int i
        for i in range(st.length):
            if st._sent[i].head == 0 and st._sent[i].dep == 0:
                st._sent[i].dep = self.root_label

    def finalize_doc(self, doc):
        doc.is_parsed = True
        if doc.vocab.lang == 'de':
            PseudoProjectivity.deprojectivize(doc)

    cdef int set_valid(self, int* output, const StateC* st) nogil:
        cdef bint[N_MOVES] is_valid
        is_valid[SHIFT] = Shift.is_valid(st, -1)
        is_valid[REDUCE] = Reduce.is_valid(st, -1)
        is_valid[LEFT] = LeftArc.is_valid(st, -1)
        is_valid[RIGHT] = RightArc.is_valid(st, -1)
        is_valid[BREAK] = Break.is_valid(st, -1)
        cdef int i
        for i in range(self.n_moves):
            output[i] = is_valid[self.c[i].move]

    cdef int set_costs(self, int* is_valid, weight_t* costs, 
                       StateClass stcls, GoldParse gold) except -1:
        cdef int i, move, label
        cdef label_cost_func_t[N_MOVES] label_cost_funcs
        cdef move_cost_func_t[N_MOVES] move_cost_funcs
        cdef weight_t[N_MOVES] move_costs
        for i in range(N_MOVES):
            move_costs[i] = -1
        move_cost_funcs[SHIFT] = Shift.move_cost
        move_cost_funcs[REDUCE] = Reduce.move_cost
        move_cost_funcs[LEFT] = LeftArc.move_cost
        move_cost_funcs[RIGHT] = RightArc.move_cost
        move_cost_funcs[BREAK] = Break.move_cost

        label_cost_funcs[SHIFT] = Shift.label_cost
        label_cost_funcs[REDUCE] = Reduce.label_cost
        label_cost_funcs[LEFT] = LeftArc.label_cost
        label_cost_funcs[RIGHT] = RightArc.label_cost
        label_cost_funcs[BREAK] = Break.label_cost

        cdef int* labels = gold.c.labels
        cdef int* heads = gold.c.heads

        n_gold = 0
        for i in range(self.n_moves):
            if self.c[i].is_valid(stcls.c, self.c[i].label):
                is_valid[i] = True
                move = self.c[i].move
                label = self.c[i].label
                if move_costs[move] == -1:
                    move_costs[move] = move_cost_funcs[move](stcls, &gold.c)
                costs[i] = move_costs[move] + label_cost_funcs[move](stcls, &gold.c, label)
                n_gold += costs[i] <= 0
            else:
                is_valid[i] = False
                costs[i] = 9000
        if n_gold == 0:
            # Check projectivity --- leading cause
            if is_nonproj_tree(gold.heads):
                raise ValueError(
                    "Could not find a gold-standard action to supervise the dependency "
                    "parser.\n"
                    "Likely cause: the tree is non-projective (i.e. it has crossing "
                    "arcs -- see spacy/syntax/nonproj.pyx for definitions)\n"
                    "The ArcEager transition system only supports projective trees.\n"
                    "To learn non-projective representations, transform the data "
                    "before training and after parsing. Either pass make_projective=True "
                    "to the GoldParse class, or use PseudoProjectivity.preprocess_training_data")
            else:
                print(gold.words)
                print(gold.heads)
                print(gold.labels)
                raise ValueError(
                    "Could not find a gold-standard action to supervise the dependency "
                    "parser.\n"
                    "The GoldParse was projective.\n"
                    "The transition system has %d actions.\n" 
                    "State at failure:\n"
                    "%s" % (self.n_moves, stcls.print_state(gold.words)))
        assert n_gold >= 1
