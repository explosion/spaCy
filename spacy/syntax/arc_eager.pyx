# cython: profile=True
from __future__ import unicode_literals

from ._state cimport State
from ._state cimport has_head, get_idx, get_s0, get_n0, get_left, get_right
from ._state cimport is_final, at_eol, pop_stack, push_stack, add_dep
from ._state cimport head_in_buffer, children_in_buffer
from ._state cimport head_in_stack, children_in_stack
from ._state cimport count_left_kids

from ..structs cimport TokenC

from .transition_system cimport do_func_t, get_cost_func_t
from .transition_system cimport move_cost_func_t, label_cost_func_t
from ..gold cimport GoldParse
from ..gold cimport GoldParseC


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

    CONSTITUENT
    ADJUST

    N_MOVES


MOVE_NAMES = [None] * N_MOVES
MOVE_NAMES[SHIFT] = 'S'
MOVE_NAMES[REDUCE] = 'D'
MOVE_NAMES[LEFT] = 'L'
MOVE_NAMES[RIGHT] = 'R'
MOVE_NAMES[BREAK] = 'B'
MOVE_NAMES[CONSTITUENT] = 'C'
MOVE_NAMES[ADJUST] = 'A'


# Helper functions for the arc-eager oracle

cdef int push_cost(const State* st, const GoldParseC* gold, int target) except -1:
    # When we push a word, we can't make arcs to or from the stack. So, we lose
    # any of those arcs.
    cdef int cost = 0
    cost += head_in_stack(st, target, gold.heads)
    cost += children_in_stack(st, target, gold.heads)
    # If we can Break, we shouldn't push
    cost += Break.is_valid(st, -1) and Break.move_cost(st, gold) == 0
    return cost


cdef int pop_cost(const State* st, const GoldParseC* gold, int target) except -1:
    cdef int cost = 0
    cost += children_in_buffer(st, target, gold.heads)
    cost += head_in_buffer(st, target, gold.heads)
    return cost


cdef int arc_cost(const State* st, const GoldParseC* gold, int head, int child) except -1:
    if arc_is_gold(gold, head, child):
        return 0
    elif (child + st.sent[child].head) == gold.heads[child]:
        return 1
    elif gold.heads[child] >= st.i:
        return 1
    else:
        return 0



cdef bint arc_is_gold(const GoldParseC* gold, int head, int child) except -1:
    if gold.labels[child] == -1:
        return True
    elif _is_gold_root(gold, head) and _is_gold_root(gold, child):
        return True
    elif gold.heads[child] == head:
        return True
    else:
        return False


cdef bint label_is_gold(const GoldParseC* gold, int head, int child, int label) except -1:
    if gold.labels[child] == -1:
        return True
    elif label == -1:
        return True
    elif gold.labels[child] == label:
        return True
    else:
        return False


cdef bint _is_gold_root(const GoldParseC* gold, int word) except -1:
    return gold.labels[word] == -1 or gold.heads[word] == word
 

cdef class Shift:
    @staticmethod
    cdef bint is_valid(const State* s, int label) except -1:
        return not at_eol(s)

    @staticmethod
    cdef int transition(State* state, int label) except -1:
        # Set the dep label, in case we need it after we reduce
        if NON_MONOTONIC:
            state.sent[state.i].dep = label
        push_stack(state)

    @staticmethod
    cdef int cost(const State* s, const GoldParseC* gold, int label) except -1:
        if not Shift.is_valid(s, label):
            return 9000
        return Shift.move_cost(s, gold) + Shift.label_cost(s, gold, label)

    @staticmethod
    cdef int move_cost(const State* s, const GoldParseC* gold) except -1:
        return push_cost(s, gold, s.i)

    @staticmethod
    cdef int label_cost(const State* s, const GoldParseC* gold, int label) except -1:
        return 0


cdef class Reduce:
    @staticmethod
    cdef bint is_valid(const State* s, int label) except -1:
        if NON_MONOTONIC:
            return s.stack_len >= 2 #and not missing_brackets(s)
        else:
            return s.stack_len >= 2 and has_head(get_s0(s))

    @staticmethod
    cdef int transition(State* state, int label) except -1:
        if NON_MONOTONIC and not has_head(get_s0(state)) and state.stack_len >= 2:
            add_dep(state, state.stack[-1], state.stack[0], get_s0(state).dep)
        pop_stack(state)

    @staticmethod
    cdef int cost(const State* s, const GoldParseC* gold, int label) except -1:
        if not Reduce.is_valid(s, label):
            return 9000
        return Reduce.move_cost(s, gold) + Reduce.label_cost(s, gold, label)

    @staticmethod
    cdef int move_cost(const State* s, const GoldParseC* gold) except -1:
        if NON_MONOTONIC:
            return pop_cost(s, gold, s.stack[0])
        else:
            return children_in_buffer(s, s.stack[0], gold.heads)

    @staticmethod
    cdef int label_cost(const State* s, const GoldParseC* gold, int label) except -1:
        return 0


cdef class LeftArc:
    @staticmethod
    cdef bint is_valid(const State* s, int label) except -1:
        if NON_MONOTONIC:
            return s.stack_len >= 1 #and not missing_brackets(s)
        else:
            return s.stack_len >= 1 and not has_head(get_s0(s))

    @staticmethod
    cdef int transition(State* state, int label) except -1:
        # Interpret left-arcs from EOL as attachment to root
        if at_eol(state):
            add_dep(state, state.stack[0], state.stack[0], label)
        else:
            add_dep(state, state.i, state.stack[0], label)
        pop_stack(state)

    @staticmethod
    cdef int cost(const State* s, const GoldParseC* gold, int label) except -1:
        if not LeftArc.is_valid(s, label):
            return 9000
        return LeftArc.move_cost(s, gold) + LeftArc.label_cost(s, gold, label)

    @staticmethod
    cdef int move_cost(const State* s, const GoldParseC* gold) except -1:
        if not LeftArc.is_valid(s, -1):
            return 9000
        elif arc_is_gold(gold, s.i, s.stack[0]):
            return 0
        else:
            return pop_cost(s, gold, s.stack[0]) + arc_cost(s, gold, s.i, s.stack[0])

    @staticmethod
    cdef int label_cost(const State* s, const GoldParseC* gold, int label) except -1:
        return arc_is_gold(gold, s.i, s.stack[0]) and not label_is_gold(gold, s.i, s.stack[0], label)


cdef class RightArc:
    @staticmethod
    cdef bint is_valid(const State* s, int label) except -1:
        return s.stack_len >= 1 and not at_eol(s)

    @staticmethod
    cdef int transition(State* state, int label) except -1:
        add_dep(state, state.stack[0], state.i, label)
        push_stack(state)

    @staticmethod
    cdef int cost(const State* s, const GoldParseC* gold, int label) except -1:
        if not RightArc.is_valid(s, label):
            return 9000
        return RightArc.move_cost(s, gold) + RightArc.label_cost(s, gold, label)

    @staticmethod
    cdef int move_cost(const State* s, const GoldParseC* gold) except -1:
        if arc_is_gold(gold, s.stack[0], s.i):
            return 0
        else:
            return push_cost(s, gold, s.i) + arc_cost(s, gold, s.stack[0], s.i)

    @staticmethod
    cdef int label_cost(const State* s, const GoldParseC* gold, int label) except -1:
        return arc_is_gold(gold, s.stack[0], s.i) and not label_is_gold(gold, s.stack[0], s.i, label)


cdef class Break:
    @staticmethod
    cdef bint is_valid(const State* s, int label) except -1:
        cdef int i
        if not USE_BREAK:
            return False
        elif at_eol(s):
            return False
        elif s.stack_len < 1:
            return False
        elif NON_MONOTONIC:
            return True
        else:
            # In the Break transition paper, they have this constraint that prevents
            # Break if stack is disconnected. But, if we're doing non-monotonic parsing,
            # we prefer to relax this constraint. This is helpful in parsing whole
            # documents, because then we don't get stuck with words on the stack.
            seen_headless = False
            for i in range(s.stack_len):
                if s.sent[s.stack[-i]].head == 0:
                    if seen_headless:
                        return False
                    else:
                        seen_headless = True
            # TODO: Constituency constraints
            return True

    @staticmethod
    cdef int transition(State* state, int label) except -1:
        state.sent[state.i-1].sent_end = True
        while state.stack_len != 0:
            if get_s0(state).head == 0:
                get_s0(state).dep = label
            state.stack -= 1
            state.stack_len -= 1

    @staticmethod
    cdef int cost(const State* s, const GoldParseC* gold, int label) except -1:
        if not Break.is_valid(s, label):
            return 9000
        else:
            return Break.move_cost(s, gold) + Break.label_cost(s, gold, label)

    @staticmethod
    cdef int move_cost(const State* s, const GoldParseC* gold) except -1:
        # When we break, we Reduce all of the words on the stack.
        cdef int cost = 0
        # Number of deps between S0...Sn and N0...Nn
        for i in range(s.i, s.sent_len):
            cost += children_in_stack(s, i, gold.heads)
            cost += head_in_stack(s, i, gold.heads)
        return cost
    
    @staticmethod
    cdef int label_cost(const State* s, const GoldParseC* gold, int label) except -1:
        return 0


cdef class Constituent:
    @staticmethod
    cdef bint is_valid(const State* s, int label) except -1:
        if s.stack_len < 1:
            return False
        return False
    #else:
    #    # If all stack elements are popped, can't constituent
    #    for i in range(s.ctnts.stack_len):
    #        if not s.ctnts.is_popped[-i]:
    #            return True
    #    else:
    #        return False

    @staticmethod
    cdef int transition(State* state, int label) except -1:
        return False
        #cdef Constituent* bracket = new_bracket(state.ctnts)

        #bracket.parent = NULL
        #bracket.label = self.label
        #bracket.head = get_s0(state)
        #bracket.length = 0

        #attach(bracket, state.ctnts.stack)
        # Attach rightward children. They're in the brackets array somewhere
        # between here and B0.
        #cdef Constituent* node
        #cdef const TokenC* node_gov
        #for i in range(1, bracket - state.ctnts.stack):
        #    node = bracket - i
        #    node_gov = node.head + node.head.head
        #    if node_gov == bracket.head:
        #        attach(bracket, node)

    @staticmethod
    cdef int cost(const State* s, const GoldParseC* gold, int label) except -1:
        if not Constituent.is_valid(s, label):
            return 9000
        raise Exception("Constituent move should be disabled currently")
        # The gold standard is indexed by end, then by start, then a set of labels
        #brackets = gold.brackets(get_s0(s).r_edge, {})
        #if not brackets:
        #    return 2 # 2 loss for bad bracket, only 1 for good bracket bad label
        # Index the current brackets in the state
        #existing = set()
        #for i in range(s.ctnt_len):
        #    if ctnt.end == s.r_edge and ctnt.label == self.label:
        #        existing.add(ctnt.start)
        #cdef int loss = 2
        #cdef const TokenC* child
        #cdef const TokenC* s0 = get_s0(s)
        #cdef int n_left = count_left_kids(s0)
        # Iterate over the possible start positions, and check whether we have a
        # (start, end, label) match to the gold tree
        #for i in range(1, n_left):
        #    child = get_left(s, s0, i)
        #    if child.l_edge in brackets and child.l_edge not in existing:
        #        if self.label in brackets[child.l_edge]
        #            return 0
        #        else:
        #            loss = 1 # If we see the start position, set loss to 1
        #return loss

    @staticmethod
    cdef int move_cost(const State* s, const GoldParseC* gold) except -1:
        if not Constituent.is_valid(s, -1):
            return 9000
        raise Exception("Constituent move should be disabled currently")
    
    @staticmethod
    cdef int label_cost(const State* s, const GoldParseC* gold, int label) except -1:
        return 0



cdef class Adjust:
    @staticmethod
    cdef bint is_valid(const State* s, int label) except -1:
        return False
        #if s.ctnts.stack_len < 2:
        #    return False

        #cdef const Constituent* b1 = s.ctnts.stack[-1]
        #cdef const Constituent* b0 = s.ctnts.stack[0]

        #if (b1.head + b1.head.head) != b0.head:
        #    return False
        #elif b0.head >= b1.head:
        #    return False
        #elif b0 >= b1:
        #    return False

    @staticmethod
    cdef int transition(State* state, int label) except -1:
        return False
        #cdef Constituent* b0 = state.ctnts.stack[0]
        #cdef Constituent* b1 = state.ctnts.stack[1]

        #assert (b1.head + b1.head.head) == b0.head
        #assert b0.head < b1.head
        #assert b0 < b1

        #attach(b0, b1)
        ## Pop B1 from stack, but keep B0 on top
        #state.ctnts.stack -= 1
        #state.ctnts.stack[0] = b0

    @staticmethod
    cdef int cost(const State* s, const GoldParseC* gold, int label) except -1:
        if not Adjust.is_valid(s, label):
            return 9000
        raise Exception("Adjust move should be disabled currently")

    @staticmethod
    cdef int move_cost(const State* s, const GoldParseC* gold) except -1:
        if not Adjust.is_valid(s, -1):
            return 9000
        raise Exception("Adjust move should be disabled currently")
    
    @staticmethod
    cdef int label_cost(const State* s, const GoldParseC* gold, int label) except -1:
        return 0
        # The gold standard is indexed by end, then by start, then a set of labels
        #gold_starts = gold.brackets(get_s0(s).r_edge, {})
        # Case 1: There are 0 brackets ending at this word.
        # --> Cost is sunk, but must allow brackets to begin
        #if not gold_starts:
        #    return 0
        # Is the top bracket correct?
        #gold_labels = gold_starts.get(s.ctnt.start, set())
        # TODO: Case where we have a unary rule
        # TODO: Case where two brackets end on this word, with top bracket starting
        # before

        #cdef const TokenC* child
        #cdef const TokenC* s0 = get_s0(s)
        #cdef int n_left = count_left_kids(s0)
        #cdef int i
        # Iterate over the possible start positions, and check whether we have a
        # (start, end, label) match to the gold tree
        #for i in range(1, n_left):
        #    child = get_left(s, s0, i)
        #    if child.l_edge in brackets:
        #        if self.label in brackets[child.l_edge]:
        #            return 0
        #        else:
        #            loss = 1 # If we see the start position, set loss to 1
        #return loss


cdef class ArcEager(TransitionSystem):
    @classmethod
    def get_labels(cls, gold_parses):
        move_labels = {SHIFT: {'': True}, REDUCE: {'': True}, RIGHT: {},
                       LEFT: {'ROOT': True}, BREAK: {'ROOT': True},
                       CONSTITUENT: {}, ADJUST: {'': True}}
        for raw_text, sents in gold_parses:
            for (ids, words, tags, heads, labels, iob), ctnts in sents:
                for child, head, label in zip(ids, heads, labels):
                    if label != 'ROOT':
                        if head < child:
                            move_labels[RIGHT][label] = True
                        elif head > child:
                            move_labels[LEFT][label] = True
                for start, end, label in ctnts:
                    move_labels[CONSTITUENT][label] = True
        return move_labels

    cdef int preprocess_gold(self, GoldParse gold) except -1:
        for i in range(gold.length):
            if gold.heads[i] is None: # Missing values
                gold.c.heads[i] = i
                gold.c.labels[i] = -1
            else:
                gold.c.heads[i] = gold.heads[i]
                gold.c.labels[i] = self.strings[gold.labels[i]]
        for end, brackets in gold.brackets.items():
            for start, label_strs in brackets.items():
                gold.c.brackets[start][end] = 1
                for label_str in label_strs:
                    # Add the encoded label to the set
                    gold.brackets[end][start].add(self.strings[label_str])

    cdef Transition lookup_transition(self, object name) except *:
        if '-' in name:
            move_str, label_str = name.split('-', 1)
            label = self.label_ids[label_str]
        else:
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
        elif move == CONSTITUENT:
            t.is_valid = Constituent.is_valid
            t.do = Constituent.transition
            t.get_cost = Constituent.cost
        elif move == ADJUST:
            t.is_valid = Adjust.is_valid
            t.do = Adjust.transition
            t.get_cost = Adjust.cost
        else:
            raise Exception(move)
        return t

    cdef int initialize_state(self, State* state) except -1:
        push_stack(state)

    cdef int finalize_state(self, State* state) except -1:
        cdef int root_label = self.strings['ROOT']
        for i in range(state.sent_len):
            if state.sent[i].head == 0 and state.sent[i].dep == 0:
                state.sent[i].dep = root_label

    cdef int set_valid(self, bint* output, const State* state) except -1:
        cdef bint[N_MOVES] is_valid
        is_valid[SHIFT] = Shift.is_valid(state, -1)
        is_valid[REDUCE] = Reduce.is_valid(state, -1)
        is_valid[LEFT] = LeftArc.is_valid(state, -1)
        is_valid[RIGHT] = RightArc.is_valid(state, -1)
        is_valid[BREAK] = Break.is_valid(state, -1)
        is_valid[CONSTITUENT] = Constituent.is_valid(state, -1)
        is_valid[ADJUST] = Adjust.is_valid(state, -1)
        cdef int i
        for i in range(self.n_moves):
            output[i] = is_valid[self.c[i].move]

    cdef int set_costs(self, int* output, const State* s, GoldParse gold) except -1:
        cdef int i, move, label
        cdef label_cost_func_t[N_MOVES] label_cost_funcs
        cdef move_cost_func_t[N_MOVES] move_cost_funcs
        cdef int[N_MOVES] move_costs
        for i in range(N_MOVES):
            move_costs[i] = -1
        move_cost_funcs[SHIFT] = Shift.move_cost
        move_cost_funcs[REDUCE] = Reduce.move_cost
        move_cost_funcs[LEFT] = LeftArc.move_cost
        move_cost_funcs[RIGHT] = RightArc.move_cost
        move_cost_funcs[BREAK] = Break.move_cost
        move_cost_funcs[CONSTITUENT] = Constituent.move_cost
        move_cost_funcs[ADJUST] = Adjust.move_cost

        label_cost_funcs[SHIFT] = Shift.label_cost
        label_cost_funcs[REDUCE] = Reduce.label_cost
        label_cost_funcs[LEFT] = LeftArc.label_cost
        label_cost_funcs[RIGHT] = RightArc.label_cost
        label_cost_funcs[BREAK] = Break.label_cost
        label_cost_funcs[CONSTITUENT] = Constituent.label_cost
        label_cost_funcs[ADJUST] = Adjust.label_cost

        cdef int* labels = gold.c.labels
        cdef int* heads = gold.c.heads
        for i in range(self.n_moves):
            move = self.c[i].move
            label = self.c[i].label
            if move_costs[move] == -1:
                move_costs[move] = move_cost_funcs[move](s, &gold.c)
            output[i] = move_costs[move] + label_cost_funcs[move](s, &gold.c, label)

    cdef Transition best_valid(self, const weight_t* scores, const State* s) except *:
        cdef bint[N_MOVES] is_valid
        is_valid[SHIFT] = Shift.is_valid(s, -1)
        is_valid[REDUCE] = Reduce.is_valid(s, -1)
        is_valid[LEFT] = LeftArc.is_valid(s, -1)
        is_valid[RIGHT] = RightArc.is_valid(s, -1)
        is_valid[BREAK] = Break.is_valid(s, -1)
        is_valid[CONSTITUENT] = Constituent.is_valid(s, -1)
        is_valid[ADJUST] = Adjust.is_valid(s, -1)
        cdef Transition best
        cdef weight_t score = MIN_SCORE
        cdef int i
        for i in range(self.n_moves):
            if scores[i] > score and is_valid[self.c[i].move]:
                best = self.c[i]
                score = scores[i]
        assert best.clas < self.n_moves
        assert score > MIN_SCORE
        # Label Shift moves with the best Right-Arc label, for non-monotonic
        # actions
        if best.move == SHIFT:
            score = MIN_SCORE
            for i in range(self.n_moves):
                if self.c[i].move == RIGHT and scores[i] > score:
                    best.label = self.c[i].label
                    score = scores[i]
        return best


