# cython: profile=True
# cython: cdivision=True
# cython: infer_types=True
# coding: utf-8
from __future__ import unicode_literals

from cpython.ref cimport Py_INCREF
from cymem.cymem cimport Pool
from collections import OrderedDict
from thinc.extra.search cimport Beam

from .stateclass cimport StateClass
from ._state cimport StateC
from .nonproj import is_nonproj_tree
from .transition_system cimport move_cost_func_t, label_cost_func_t
from ..gold cimport GoldParse, GoldParseC
from ..structs cimport TokenC
from ..errors import Errors


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
    cost += Break.is_valid(stcls.c, 0) and Break.move_cost(stcls, gold) == 0
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
    if Break.is_valid(stcls.c, 0) and Break.move_cost(stcls, gold) == 0:
        cost += 1
    return cost


cdef weight_t arc_cost(StateClass stcls, const GoldParseC* gold, int head, int child) nogil:
    if arc_is_gold(gold, head, child):
        return 0
    elif stcls.H(child) == gold.heads[child]:
        return 1
    # Head in buffer
    elif gold.heads[child] >= stcls.B(0) and stcls.B(1) != 0:
        return 1
    else:
        return 0


cdef bint arc_is_gold(const GoldParseC* gold, int head, int child) nogil:
    if not gold.has_dep[child]:
        return True
    elif gold.heads[child] == head:
        return True
    else:
        return False


cdef bint label_is_gold(const GoldParseC* gold, int head, int child, attr_t label) nogil:
    if not gold.has_dep[child]:
        return True
    elif label == 0:
        return True
    elif gold.labels[child] == label:
        return True
    else:
        return False


cdef bint _is_gold_root(const GoldParseC* gold, int word) nogil:
    return gold.heads[word] == word or not gold.has_dep[word]

cdef class Shift:
    @staticmethod
    cdef bint is_valid(const StateC* st, attr_t label) nogil:
        return st.buffer_length() >= 2 and not st.shifted[st.B(0)] and st.B_(0).sent_start != 1

    @staticmethod
    cdef int transition(StateC* st, attr_t label) nogil:
        st.push()
        st.fast_forward()

    @staticmethod
    cdef weight_t cost(StateClass st, const GoldParseC* gold, attr_t label) nogil:
        return Shift.move_cost(st, gold) + Shift.label_cost(st, gold, label)

    @staticmethod
    cdef inline weight_t move_cost(StateClass s, const GoldParseC* gold) nogil:
        return push_cost(s, gold, s.B(0))

    @staticmethod
    cdef inline weight_t label_cost(StateClass s, const GoldParseC* gold, attr_t label) nogil:
        return 0


cdef class Reduce:
    @staticmethod
    cdef bint is_valid(const StateC* st, attr_t label) nogil:
        return st.stack_depth() >= 2

    @staticmethod
    cdef int transition(StateC* st, attr_t label) nogil:
        if st.has_head(st.S(0)):
            st.pop()
        else:
            st.unshift()
        st.fast_forward()

    @staticmethod
    cdef weight_t cost(StateClass s, const GoldParseC* gold, attr_t label) nogil:
        return Reduce.move_cost(s, gold) + Reduce.label_cost(s, gold, label)

    @staticmethod
    cdef inline weight_t move_cost(StateClass st, const GoldParseC* gold) nogil:
        cost = pop_cost(st, gold, st.S(0))
        if not st.has_head(st.S(0)):
            # Decrement cost for the arcs e save
            for i in range(1, st.stack_depth()):
                S_i = st.S(i)
                if gold.heads[st.S(0)] == S_i:
                    cost -= 1
                if gold.heads[S_i] == st.S(0):
                    cost -= 1
            if Break.is_valid(st.c, 0) and Break.move_cost(st, gold) == 0:
                cost -= 1
        return cost

    @staticmethod
    cdef inline weight_t label_cost(StateClass s, const GoldParseC* gold, attr_t label) nogil:
        return 0


cdef class LeftArc:
    @staticmethod
    cdef bint is_valid(const StateC* st, attr_t label) nogil:
        return st.B_(0).sent_start != 1

    @staticmethod
    cdef int transition(StateC* st, attr_t label) nogil:
        st.add_arc(st.B(0), st.S(0), label)
        st.pop()
        st.fast_forward()

    @staticmethod
    cdef weight_t cost(StateClass s, const GoldParseC* gold, attr_t label) nogil:
        return LeftArc.move_cost(s, gold) + LeftArc.label_cost(s, gold, label)

    @staticmethod
    cdef inline weight_t move_cost(StateClass s, const GoldParseC* gold) nogil:
        cdef weight_t cost = 0
        if arc_is_gold(gold, s.B(0), s.S(0)):
            # Have a negative cost if we 'recover' from the wrong dependency
            return 0 if not s.has_head(s.S(0)) else -1
        else:
            # Account for deps we might lose between S0 and stack
            if not s.has_head(s.S(0)):
                for i in range(1, s.stack_depth()):
                    cost += gold.heads[s.S(i)] == s.S(0)
                    cost += gold.heads[s.S(0)] == s.S(i)
            return cost + pop_cost(s, gold, s.S(0)) + arc_cost(s, gold, s.B(0), s.S(0))

    @staticmethod
    cdef inline weight_t label_cost(StateClass s, const GoldParseC* gold, attr_t label) nogil:
        return arc_is_gold(gold, s.B(0), s.S(0)) and not label_is_gold(gold, s.B(0), s.S(0), label)


cdef class RightArc:
    @staticmethod
    cdef bint is_valid(const StateC* st, attr_t label) nogil:
        # If there's (perhaps partial) parse pre-set, don't allow cycle.
        return st.B_(0).sent_start != 1 and st.H(st.S(0)) != st.B(0)

    @staticmethod
    cdef int transition(StateC* st, attr_t label) nogil:
        st.add_arc(st.S(0), st.B(0), label)
        st.push()
        st.fast_forward()

    @staticmethod
    cdef inline weight_t cost(StateClass s, const GoldParseC* gold, attr_t label) nogil:
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
    cdef weight_t label_cost(StateClass s, const GoldParseC* gold, attr_t label) nogil:
        return arc_is_gold(gold, s.S(0), s.B(0)) and not label_is_gold(gold, s.S(0), s.B(0), label)


cdef class Break:
    @staticmethod
    cdef bint is_valid(const StateC* st, attr_t label) nogil:
        cdef int i
        if not USE_BREAK:
            return False
        elif st.at_break():
            return False
        elif st.stack_depth() < 1:
            return False
        elif st.B_(0).l_edge < 0:
            return False
        elif st._sent[st.B_(0).l_edge].sent_start < 0:
            return False
        else:
            return True

    @staticmethod
    cdef int transition(StateC* st, attr_t label) nogil:
        st.set_break(st.B_(0).l_edge)
        st.fast_forward()

    @staticmethod
    cdef weight_t cost(StateClass s, const GoldParseC* gold, attr_t label) nogil:
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
                if cost != 0:
                    return cost
        # Check for sentence boundary --- if it's here, we can't have any deps
        # between stack and buffer, so rest of action is irrelevant.
        s0_root = _get_root(s.S(0), gold)
        b0_root = _get_root(s.B(0), gold)
        if s0_root != b0_root or s0_root == -1 or b0_root == -1:
            return cost
        else:
            return cost + 1

    @staticmethod
    cdef inline weight_t label_cost(StateClass s, const GoldParseC* gold, attr_t label) nogil:
        return 0

cdef int _get_root(int word, const GoldParseC* gold) nogil:
    while gold.heads[word] != word and gold.has_dep[word] and word >= 0:
        word = gold.heads[word]
    if not gold.has_dep[word]:
        return -1
    else:
        return word


cdef void* _init_state(Pool mem, int length, void* tokens) except NULL:
    st = new StateC(<const TokenC*>tokens, length)
    for i in range(st.length):
        if st._sent[i].dep == 0:
            st._sent[i].l_edge = i
            st._sent[i].r_edge = i
            st._sent[i].head = 0
            st._sent[i].dep = 0
            st._sent[i].l_kids = 0
            st._sent[i].r_kids = 0
    st.fast_forward()
    return <void*>st


cdef class ArcEager(TransitionSystem):
    def __init__(self, *args, **kwargs):
        TransitionSystem.__init__(self, *args, **kwargs)
        self.init_beam_state = _init_state

    @classmethod
    def get_actions(cls, **kwargs):
        actions = kwargs.get('actions', OrderedDict((
            (SHIFT, ['']),
            (REDUCE, ['']),
            (RIGHT, []),
            (LEFT, []),
            (BREAK, ['ROOT']))
        ))
        seen_actions = set()
        for label in kwargs.get('left_labels', []):
            if label.upper() != 'ROOT':
                if (LEFT, label) not in seen_actions:
                    actions[LEFT].append(label)
                    seen_actions.add((LEFT, label))
        for label in kwargs.get('right_labels', []):
            if label.upper() != 'ROOT':
                if (RIGHT, label) not in seen_actions:
                    actions[RIGHT].append(label)
                    seen_actions.add((RIGHT, label))

        for raw_text, sents in kwargs.get('gold_parses', []):
            for (ids, words, tags, heads, labels, iob), ctnts in sents:
                for child, head, label in zip(ids, heads, labels):
                    if label.upper() == 'ROOT':
                        label = 'ROOT'
                    if label != 'ROOT':
                        if head < child:
                            if (RIGHT, label) not in seen_actions:
                                actions[RIGHT].append(label)
                                seen_actions.add((RIGHT, label))
                        elif head > child:
                            if (LEFT, label) not in seen_actions:
                                actions[LEFT].append(label)
                                seen_actions.add((LEFT, label))
        return actions

    property action_types:
        def __get__(self):
            return (SHIFT, REDUCE, LEFT, RIGHT, BREAK)

    def is_gold_parse(self, StateClass state, GoldParse gold):
        predicted = set()
        truth = set()
        for i in range(gold.length):
            if gold.cand_to_gold[i] is None:
                continue
            if state.safe_get(i).dep:
                predicted.add((i, state.H(i),
                              self.strings[state.safe_get(i).dep]))
            else:
                predicted.add((i, state.H(i), 'ROOT'))
            id_, word, tag, head, dep, ner = gold.orig_annot[gold.cand_to_gold[i]]
            truth.add((id_, head, dep))
        return truth == predicted

    def has_gold(self, GoldParse gold, start=0, end=None):
        end = end or len(gold.heads)
        if all([tag is None for tag in gold.heads[start:end]]):
            return False
        else:
            return True

    def preprocess_gold(self, GoldParse gold):
        if not self.has_gold(gold):
            return None
        for i in range(gold.length):
            # Missing values
            if gold.heads[i] is None or gold.labels[i] is None:
                gold.c.heads[i] = i
                gold.c.has_dep[i] = False
            else:
                label = gold.labels[i]
                gold.c.has_dep[i] = True
                if label.upper() == 'ROOT':
                    label = 'ROOT'
                gold.c.heads[i] = gold.heads[i]
                gold.c.labels[i] = self.strings.add(label)
        return gold

    def get_beam_parses(self, Beam beam):
        parses = []
        probs = beam.probs
        for i in range(beam.size):
            state = <StateC*>beam.at(i)
            if state.is_final():
                self.finalize_state(state)
                prob = probs[i]
                parse = []
                for j in range(state.length):
                    head = state.H(j)
                    label = self.strings[state._sent[j].dep]
                    parse.append((head, j, label))
                parses.append((prob, parse))
        return parses

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
        return Transition(clas=0, move=MISSING, label=0)

    def move_name(self, int move, attr_t label):
        label_str = self.strings[label]
        if label_str:
            return MOVE_NAMES[move] + '-' + label_str
        else:
            return MOVE_NAMES[move]

    cdef Transition init_transition(self, int clas, int move, attr_t label) except *:
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
            raise ValueError(Errors.E019.format(action=move, src='arc_eager'))
        return t

    cdef int initialize_state(self, StateC* st) nogil:
        for i in range(st.length):
            if st._sent[i].dep == 0:
                st._sent[i].l_edge = i
                st._sent[i].r_edge = i
                st._sent[i].head = 0
                st._sent[i].dep = 0
                st._sent[i].l_kids = 0
                st._sent[i].r_kids = 0
        st.fast_forward()

    cdef int finalize_state(self, StateC* st) nogil:
        cdef int i
        for i in range(st.length):
            if st._sent[i].head == 0:
                st._sent[i].dep = self.root_label

    def finalize_doc(self, doc):
        doc.is_parsed = True

    cdef int set_valid(self, int* output, const StateC* st) nogil:
        cdef bint[N_MOVES] is_valid
        is_valid[SHIFT] = Shift.is_valid(st, 0)
        is_valid[REDUCE] = Reduce.is_valid(st, 0)
        is_valid[LEFT] = LeftArc.is_valid(st, 0)
        is_valid[RIGHT] = RightArc.is_valid(st, 0)
        is_valid[BREAK] = Break.is_valid(st, 0)
        cdef int i
        for i in range(self.n_moves):
            output[i] = is_valid[self.c[i].move]

    cdef int set_costs(self, int* is_valid, weight_t* costs,
                       StateClass stcls, GoldParse gold) except -1:
        cdef int i, move
        cdef attr_t label
        cdef label_cost_func_t[N_MOVES] label_cost_funcs
        cdef move_cost_func_t[N_MOVES] move_cost_funcs
        cdef weight_t[N_MOVES] move_costs
        for i in range(N_MOVES):
            move_costs[i] = 9000
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

        cdef attr_t* labels = gold.c.labels
        cdef int* heads = gold.c.heads

        n_gold = 0
        for i in range(self.n_moves):
            if self.c[i].is_valid(stcls.c, self.c[i].label):
                is_valid[i] = True
                move = self.c[i].move
                label = self.c[i].label
                if move_costs[move] == 9000:
                    move_costs[move] = move_cost_funcs[move](stcls, &gold.c)
                costs[i] = move_costs[move] + label_cost_funcs[move](stcls, &gold.c, label)
                n_gold += costs[i] <= 0
            else:
                is_valid[i] = False
                costs[i] = 9000
        if n_gold < 1:
            # Check projectivity --- leading cause
            if is_nonproj_tree(gold.heads):
                raise ValueError(Errors.E020)
            else:
                failure_state = stcls.print_state(gold.words)
                raise ValueError(Errors.E021.format(n_actions=self.n_moves,
                                                    state=failure_state))

    def get_beam_annot(self, Beam beam):
        length = (<StateC*>beam.at(0)).length
        heads = [{} for _ in range(length)]
        deps = [{} for _ in range(length)]
        probs = beam.probs
        for i in range(beam.size):
            state = <StateC*>beam.at(i)
            self.finalize_state(state)
            if state.is_final():
                prob = probs[i]
                for j in range(state.length):
                    head = j + state._sent[j].head
                    dep = state._sent[j].dep
                    heads[j].setdefault(head, 0.0)
                    heads[j][head] += prob
                    deps[j].setdefault(dep, 0.0)
                    deps[j][dep] += prob
        return heads, deps
