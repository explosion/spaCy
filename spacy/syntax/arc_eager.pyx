# cython: profile=True, cdivision=True, infer_types=True
from cpython.ref cimport Py_INCREF
from cymem.cymem cimport Pool
from thinc.extra.search cimport Beam

from collections import defaultdict, Counter
import json

from ..typedefs cimport hash_t, attr_t
from ..strings cimport hash_string
from ..structs cimport TokenC
from ..tokens.doc cimport Doc, set_children_from_heads
from .stateclass cimport StateClass
from ._state cimport StateC
from .transition_system cimport move_cost_func_t, label_cost_func_t

from ..errors import Errors
from .nonproj import is_nonproj_tree
from . import nonproj


# Calculate cost as gold/not gold. We don't use scalar value anyway.
cdef int BINARY_COSTS = 1
cdef weight_t MIN_SCORE = -90000
cdef attr_t SUBTOK_LABEL = hash_string(u'subtok')

DEF NON_MONOTONIC = True
DEF USE_BREAK = True

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


cdef enum:
    HEAD_ON_STACK = 0
    HEAD_IN_BUFFER
    IS_SENT_START
    HEAD_UNKNOWN


cdef struct GoldParseStateC:
    char* state_bits
    attr_t* labels
    int32_t* heads
    int32_t* n_kids_in_buffer
    int32_t* n_kids_on_stack
    int32_t length
    int32_t stride


cdef int check_state_flag(char state_bits, char flag) nogil:
    cdef char one = 1
    return state_bits & (one << flag)


cdef int set_state_flag(char state_bits, char flag, int value) nogil:
    cdef char one = 1
    if value:
        return state_bits | (one << flag)
    else:
        return state_bits & ~(one << flag)


cdef int is_head_on_stack(GoldParseStateC gold, int i) nogil:
    return check_state_gold(gold.state_bits[i], HEAD_ON_STACK)


cdef int is_head_in_buffer(GoldParseStateC gold, int i) nogil:
    return check_state_gold(gold.state_bits[i], HEAD_IN_BUFFER)


cdef int is_sent_start(GoldParseStateC gold, int i) nogil:
    return check_state_gold(gold.state_bits[i], IS_SENT_START)


cdef int is_head_unknown(GoldParseStateC gold, int i) nogil:
    return check_state_gold(gold.state_bits[i], HEAD_UNKNOWN)


# Helper functions for the arc-eager oracle

cdef weight_t push_cost(StateClass stcls, const GoldParseStateC* gold, int target) nogil:
    cdef weight_t cost = 0
    if is_head_in_stack(gold[0], target):
        cost += 1
    cost += gold.n_kids_in_buffer[target]
    if Break.is_valid(stcls.c, 0) and Break.move_cost(stcls, gold) == 0:
        cost += 1
    return cost


cdef weight_t pop_cost(StateClass stcls, const GoldParseStateC* gold, int target) nogil:
    cdef weight_t cost = 0
    if is_head_in_buffer(gold[0], target):
        cost += 1
    cost += gold[0].n_kids_in_buffer[target]
    if Break.is_valid(stcls.c, 0) and Break.move_cost(stcls, gold) == 0:
        cost += 1
    return cost


cdef weight_t arc_cost(StateClass stcls, const GoldParseStateC* gold, int head, int child) nogil:
    if arc_is_gold(gold, head, child):
        return 0
    elif stcls.H(child) == gold.heads[child]:
        return 1
    # Head in buffer
    elif gold.heads[child] >= stcls.B(0) and stcls.B(1) != 0:
        return 1
    else:
        return 0


cdef bint arc_is_gold(const GoldParseStateC* gold, int head, int child) nogil:
    if is_head_unknown(gold[0], child):
        return True
    elif gold.heads[child] == head:
        return True
    else:
        return False


cdef bint label_is_gold(const GoldParseStateC* gold, int head, int child, attr_t label) nogil:
    if is_head_unknown(gold[0], child):
        return True
    elif label == 0:
        return True
    elif gold.labels[child] == label:
        return True
    else:
        return False


cdef bint _is_gold_root(const GoldParseStateC* gold, int word) nogil:
    return gold.heads[word] == word or is_head_unknown(gold[0], word)


cdef class Shift:
    @staticmethod
    cdef bint is_valid(const StateC* st, attr_t label) nogil:
        sent_start = st._sent[st.B_(0).l_edge].sent_start
        return st.buffer_length() >= 2 and not st.shifted[st.B(0)] and sent_start != 1

    @staticmethod
    cdef int transition(StateC* st, attr_t label) nogil:
        st.push()
        st.fast_forward()

    @staticmethod
    cdef weight_t cost(StateClass st, const void* _gold, attr_t label) nogil:
        gold = <const GoldParseStateC*>_gold
        return Shift.move_cost(st, gold) + Shift.label_cost(st, gold, label)

    @staticmethod
    cdef inline weight_t move_cost(StateClass s, const GoldParseStateC* gold) nogil:
        return push_cost(s, gold, s.B(0))

    @staticmethod
    cdef inline weight_t label_cost(StateClass s, const GoldParseStateC* gold, attr_t label) nogil:
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
    cdef weight_t cost(StateClass s, const void* _gold, attr_t label) nogil:
        gold = <const GoldParseStateC*>_gold
        return Reduce.move_cost(s, gold) + Reduce.label_cost(s, gold, label)

    @staticmethod
    cdef inline weight_t move_cost(StateClass st, const GoldParseStateC* gold) nogil:
        s0 = st.S(0)
        cost = pop_cost(st, gold, s0)
        return_to_buffer = not st.has_head(s0)
        if return_to_buffer:
            # Decrement cost for the arcs we save, as we'll be putting this
            # back to the buffer
            if is_head_in_stack(gold[0], s0):
                cost -= 1
            cost -= gold.n_kids_in_stack[s0]
            if Break.is_valid(st.c, 0) and Break.move_cost(st, gold) == 0:
                cost -= 1
        return cost

    @staticmethod
    cdef inline weight_t label_cost(StateClass s, const GoldParseStateC* gold, attr_t label) nogil:
        return 0


cdef class LeftArc:
    @staticmethod
    cdef bint is_valid(const StateC* st, attr_t label) nogil:
        if label == SUBTOK_LABEL and st.S(0) != (st.B(0)-1):
            return 0
        sent_start = st._sent[st.B_(0).l_edge].sent_start
        return sent_start != 1

    @staticmethod
    cdef int transition(StateC* st, attr_t label) nogil:
        st.add_arc(st.B(0), st.S(0), label)
        st.pop()
        st.fast_forward()

    @staticmethod
    cdef inline weight_t cost(StateClass s, const void* gold, attr_t label) nogil:
        gold = <const GoldParseStateC*>_gold
        return RightArc.move_cost(s, gold) + RightArc.label_cost(s, gold, label)

    @staticmethod
    cdef inline weight_t move_cost(StateClass s, const GoldParseStateC* gold) nogil:
        if arc_is_gold(gold, s.S(0), s.B(0)):
            return 0
        elif s.c.shifted[s.B(0)]:
            return push_cost(s, gold, s.B(0))
        else:
            return push_cost(s, gold, s.B(0)) + arc_cost(s, gold, s.S(0), s.B(0))

    @staticmethod
    cdef weight_t label_cost(StateClass s, const GoldParseStateC* gold, attr_t label) nogil:
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
    cdef weight_t cost(StateClass s, const void* _gold, attr_t label) nogil:
        gold = <const GoldParseStateC*>_gold
        return Break.move_cost(s, gold) + Break.label_cost(s, gold, label)

    @staticmethod
    cdef inline weight_t move_cost(StateClass s, const GoldParseStateC* gold) nogil:
        cdef weight_t cost = 0
        cdef int i, j, S_i, B_i
        for i in range(s.stack_depth()):
            S_i = s.S(i)
            cost += gold.n_kids_in_buffer[S_i]
            if is_head_in_buffer(gold[0], S_i):
                cost += 1
        # Check for sentence boundary --- if it's here, we can't have any deps
        # between stack and buffer, so rest of action is irrelevant.
        s0_root = _get_root(s.S(0), gold)
        b0_root = _get_root(s.B(0), gold)
        if s0_root != b0_root or s0_root == -1 or b0_root == -1:
            return cost
        else:
            return cost + 1

    @staticmethod
    cdef inline weight_t label_cost(StateClass s, const GoldParseStateC* gold, attr_t label) nogil:
        return 0

cdef int _get_root(int word, const GoldParseStateC* gold) nogil:
    if is_head_unset(gold[0], word):
        return -1
    while gold.heads[word] != word and word >= 0:
        word = gold.heads[word]
        if is_head_unset(gold[0], word):
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


cdef int _del_state(Pool mem, void* state, void* x) except -1:
    cdef StateC* st = <StateC*>state
    del st


cdef class ArcEager(TransitionSystem):
    def __init__(self, *args, **kwargs):
        TransitionSystem.__init__(self, *args, **kwargs)
        self.init_beam_state = _init_state
        self.del_beam_state = _del_state

    @classmethod
    def get_actions(cls, **kwargs):
        min_freq = kwargs.get('min_freq', None)
        actions = defaultdict(lambda: Counter())
        actions[SHIFT][''] = 1
        actions[REDUCE][''] = 1
        for label in kwargs.get('left_labels', []):
            actions[LEFT][label] = 1
            actions[SHIFT][label] = 1
        for label in kwargs.get('right_labels', []):
            actions[RIGHT][label] = 1
            actions[REDUCE][label] = 1
        for example in kwargs.get('gold_parses', []):
            heads, labels = nonproj.projectivize(example.token_annotation.heads,
                                                 example.token_annotation.deps)
            for child, head, label in zip(example.token_annotation.ids, heads, labels):
                if label.upper() == 'ROOT' :
                    label = 'ROOT'
                if head == child:
                    actions[BREAK][label] += 1
                elif head < child:
                    actions[RIGHT][label] += 1
                    actions[REDUCE][''] += 1
                elif head > child:
                    actions[LEFT][label] += 1
                    actions[SHIFT][''] += 1
        if min_freq is not None:
            for action, label_freqs in actions.items():
                for label, freq in list(label_freqs.items()):
                    if freq < min_freq:
                        label_freqs.pop(label)
        # Ensure these actions are present
        actions[BREAK].setdefault('ROOT', 0)
        if kwargs.get("learn_tokens") is True:
            actions[RIGHT].setdefault('subtok', 0)
            actions[LEFT].setdefault('subtok', 0)
        # Used for backoff
        actions[RIGHT].setdefault('dep', 0)
        actions[LEFT].setdefault('dep', 0)
        return actions

    @property
    def action_types(self):
        return (SHIFT, REDUCE, LEFT, RIGHT, BREAK)

    def get_cost(self, StateClass state, NewExample gold, action):
        raise NotImplementedError

    def transition(self, StateClass state, action):
        cdef Transition t = self.lookup_transition(action)
        t.do(state.c, t.label)
        return state

    def is_gold_parse(self, StateClass state, gold):
        raise NotImplementedError

    def has_gold(self, gold, start=0, end=None):
        raise NotImplementedError

    def preprocess_gold(self, gold):
        raise NotImplementedError

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

    cdef Transition lookup_transition(self, object name_or_id) except *:
        if isinstance(name_or_id, int):
            return self.c[name_or_id]
        name = name_or_id
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

    def class_name(self, int i):
        return self.move_name(self.c[i].move, self.c[i].label)

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

    def finalize_doc(self, Doc doc):
        doc.is_parsed = True
        set_children_from_heads(doc.c, doc.length)

    cdef int set_valid(self, int* output, const StateC* st) nogil:
        cdef bint[N_MOVES] is_valid
        is_valid[SHIFT] = Shift.is_valid(st, 0)
        is_valid[REDUCE] = Reduce.is_valid(st, 0)
        is_valid[LEFT] = LeftArc.is_valid(st, 0)
        is_valid[RIGHT] = RightArc.is_valid(st, 0)
        is_valid[BREAK] = Break.is_valid(st, 0)
        cdef int i
        for i in range(self.n_moves):
            if self.c[i].label == SUBTOK_LABEL:
                output[i] = self.c[i].is_valid(st, self.c[i].label)
            else:
                output[i] = is_valid[self.c[i].move]

    cdef int set_costs(self, int* is_valid, weight_t* costs,
                       StateClass stcls, NewExample example) except -1:
        cdef Pool mem = Pool()
        gold_state = create_gold_state(mem, stcls, example)
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
                    move_costs[move] = move_cost_funcs[move](stcls, gold_state)
                costs[i] = move_costs[move] + label_cost_funcs[move](stcls, gold_state, label)
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
