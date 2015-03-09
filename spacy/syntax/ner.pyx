from __future__ import unicode_literals

from ._state cimport State

from .transition_system cimport Transition
from .transition_system cimport do_func_t

from ..structs cimport TokenC, Entity

from thinc.typedefs cimport weight_t
from .conll cimport GoldParse
from .ner_util import iob_to_biluo


cdef enum:
    MISSING
    BEGIN
    IN
    LAST
    UNIT
    OUT
    N_MOVES


cdef do_func_t[N_MOVES] do_funcs


cdef bint entity_is_open(const State *s) except -1:
    return s.sent[s.i - 1].ent.tag >= 1


cdef bint _entity_is_sunk(const State *s, Transition* golds) except -1:
    if not entity_is_open(s):
        return False

    cdef const Entity* curr = &s.sent[s.i - 1].ent
    cdef const Transition* gold = &golds[(s.i - 1) + curr.start]
    if gold.move != BEGIN and gold.move != UNIT:
        return True
    elif gold.label != s.ent.label:
        return True
    else:
        return False


cdef int _is_valid(int act, int label, const State* s) except -1:
    if act == BEGIN:
        return not entity_is_open(s)
    elif act == IN:
        return entity_is_open(s) and s.ent.label == label
    elif act == LAST:
        return entity_is_open(s) and s.ent.label == label
    elif act == UNIT:
        return not entity_is_open(s)
    elif act == OUT:
        return not entity_is_open(s)
    else:
        raise UnknownMove(act, label)


cdef class BiluoPushDown(TransitionSystem):
    @classmethod
    def get_labels(cls, gold_tuples):
        move_labels = {BEGIN: {}, IN: {}, LAST: {}, UNIT: {}, OUT: {'ROOT': True}}
        moves = ('-', 'B', 'I', 'L', 'U')
        for (raw_text, toks, (ids, tags, heads, labels, iob)) in gold_tuples:
            for i, ner_tag in enumerate(iob_to_biluo(iob)):
                if ner_tag != 'O' and ner_tag != '-':
                    move_str, label = ner_tag.split('-')
                    move_labels[moves.index(move_str)][label] = True
        return move_labels

    cdef Transition init_transition(self, int clas, int move, int label) except *:
        # TODO: Apparent Cython bug here when we try to use the Transition()
        # constructor with the function pointers
        cdef Transition t
        t.score = 0
        t.clas = clas
        t.move = move
        t.label = label
        t.do = do_funcs[move]
        t.get_cost = _get_cost
        return t

    cdef Transition best_valid(self, const weight_t* scores, const State* s) except *:
        cdef int best = -1
        cdef weight_t score = -90000
        cdef const Transition* m
        cdef int i
        for i in range(self.n_moves):
            m = &self.c[i]
            if _is_valid(m.move, m.label, s) and scores[i] > score:
                best = i
                score = scores[i]
        assert best >= 0
        cdef Transition t = self.c[best]
        t.score = score
        return t


cdef int _get_cost(const Transition* self, const State* s, GoldParse gold) except -1:
    if not _is_valid(self.move, self.label, s):
        return 9000
    cdef bint is_sunk = _entity_is_sunk(s, gold.ner)
    cdef int next_act = gold.ner[s.i+1].move if s.i < s.sent_len else OUT
    return not _is_gold(self.move, self.label, gold.ner[s.i].move, gold.ner[s.i].label,
                        next_act, is_sunk)

cdef bint _is_gold(int act, int tag, int g_act, int g_tag,
                   int next_act, bint is_sunk):
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


cdef int _do_begin(const Transition* self, State* s) except -1:
    s.ent += 1
    s.ents_len += 1
    s.ent.start = s.i
    s.ent.label = self.label
    s.sent[s.i].ent.tag = self.clas 
    s.i += 1


cdef int _do_in(const Transition* self, State* s) except -1:
    s.sent[s.i].ent.tag = self.clas 
    s.i += 1


cdef int _do_last(const Transition* self, State* s) except -1:
    s.ent.end = s.i+1
    s.sent[s.i].ent.tag = self.clas 
    s.i += 1


cdef int _do_unit(const Transition* self, State* s) except -1:
    s.ent += 1
    s.ents_len += 1
    s.ent.start = s.i
    s.ent.label = self.label
    s.ent.end = s.i+1
    s.sent[s.i].ent.tag = self.clas 
    s.i += 1


cdef int _do_out(const Transition* self, State* s) except -1:
    s.sent[s.i].ent.tag = self.clas 
    s.i += 1


do_funcs[BEGIN] = _do_begin
do_funcs[IN] = _do_in
do_funcs[LAST] = _do_last
do_funcs[UNIT] = _do_unit
do_funcs[OUT] = _do_out


class OracleError(Exception):
    pass


class UnknownMove(Exception):
    pass


