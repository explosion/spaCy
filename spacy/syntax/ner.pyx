from __future__ import unicode_literals

from .transition_system cimport Transition
from .transition_system cimport do_func_t

from ..structs cimport TokenC, Entity

from thinc.typedefs cimport weight_t
from ..gold cimport GoldParseC
from ..gold cimport GoldParse
from ..attrs cimport ENT_TYPE, ENT_IOB

from .stateclass cimport StateClass
from ._state cimport StateC


cdef enum:
    MISSING
    BEGIN
    IN
    LAST
    UNIT
    OUT
    N_MOVES


MOVE_NAMES = [None] * N_MOVES
MOVE_NAMES[MISSING] = 'M'
MOVE_NAMES[BEGIN] = 'B'
MOVE_NAMES[IN] = 'I'
MOVE_NAMES[LAST] = 'L'
MOVE_NAMES[UNIT] = 'U'
MOVE_NAMES[OUT] = 'O'


cdef do_func_t[N_MOVES] do_funcs


cdef bint _entity_is_sunk(StateClass st, Transition* golds) nogil:
    if not st.entity_is_open():
        return False

    cdef const Transition* gold = &golds[st.E(0)]
    if gold.move != BEGIN and gold.move != UNIT:
        return True
    elif gold.label != st.E_(0).ent_type:
        return True
    else:
        return False


cdef class BiluoPushDown(TransitionSystem):
    @classmethod
    def get_actions(cls, **kwargs):
        actions = kwargs.get('actions', 
                    {
                        MISSING: {'': True},
                        BEGIN: {},
                        IN: {},
                        LAST: {},
                        UNIT: {},
                        OUT: {'': True}
                    })
        for entity_type in kwargs.get('entity_types', []):
            for action in (BEGIN, IN, LAST, UNIT):
                actions[action][entity_type] = True
        moves = ('M', 'B', 'I', 'L', 'U')
        for raw_text, sents in kwargs.get('gold_parses', []):
            for (ids, words, tags, heads, labels, biluo), _ in sents:
                for i, ner_tag in enumerate(biluo):
                    if ner_tag != 'O' and ner_tag != '-':
                        if ner_tag.count('-') != 1:
                            raise ValueError(ner_tag)
                        _, label = ner_tag.split('-')
                        for move_str in ('B', 'I', 'L', 'U'):
                            actions[moves.index(move_str)][label] = True
        return actions

    property action_types:
        def __get__(self):
            return (BEGIN, IN, LAST, UNIT, OUT)

    def move_name(self, int move, int label):
        if move == OUT:
            return 'O'
        elif move == 'MISSING':
            return 'M'
        else:
            return MOVE_NAMES[move] + '-' + self.strings[label]

    cdef int preprocess_gold(self, GoldParse gold) except -1:
        for i in range(gold.length):
            gold.c.ner[i] = self.lookup_transition(gold.ner[i])
            # Count frequencies, for use in encoder
            if gold.c.ner[i].move in (BEGIN, UNIT):
                self.freqs[ENT_IOB][3] += 1
                self.freqs[ENT_TYPE][gold.c.ner[i].label] += 1
            elif gold.c.ner[i].move in (IN, LAST):
                self.freqs[ENT_IOB][2] += 1
                self.freqs[ENT_TYPE][0] += 1
            elif gold.c.ner[i].move == OUT:
                self.freqs[ENT_IOB][1] += 1
                self.freqs[ENT_TYPE][0] += 1
            else:
                self.freqs[ENT_IOB][1] += 1
                self.freqs[ENT_TYPE][0] += 1

    cdef Transition lookup_transition(self, object name) except *:
        if name == '-':
            move_str = 'M'
            label = 0
        elif '-' in name:
            move_str, label_str = name.split('-', 1)
            label = self.strings[label_str]
        else:
            move_str = name
            label = 0
        move = MOVE_NAMES.index(move_str)
        for i in range(self.n_moves):
            if self.c[i].move == move and self.c[i].label == label:
                return self.c[i]
        else:
            raise KeyError(name)

    cdef Transition init_transition(self, int clas, int move, int label) except *:
        # TODO: Apparent Cython bug here when we try to use the Transition()
        # constructor with the function pointers
        cdef Transition t
        t.score = 0
        t.clas = clas
        t.move = move
        t.label = label
        if move == MISSING:
            t.is_valid = Missing.is_valid
            t.do = Missing.transition
            t.get_cost = Missing.cost
        elif move == BEGIN:
            t.is_valid = Begin.is_valid
            t.do = Begin.transition
            t.get_cost = Begin.cost
        elif move == IN:
            t.is_valid = In.is_valid
            t.do = In.transition
            t.get_cost = In.cost
        elif move == LAST:
            t.is_valid = Last.is_valid
            t.do = Last.transition
            t.get_cost = Last.cost
        elif move == UNIT:
            t.is_valid = Unit.is_valid
            t.do = Unit.transition
            t.get_cost = Unit.cost
        elif move == OUT:
            t.is_valid = Out.is_valid
            t.do = Out.transition
            t.get_cost = Out.cost
        else:
            raise Exception(move)
        return t

    cdef int initialize_state(self, StateC* st) nogil:
        for i in range(st.length):
            if st._sent[i].ent_type != 0:
                with gil:
                    self.add_action(BEGIN, st._sent[i].ent_type)
                    self.add_action(IN, st._sent[i].ent_type)
                    self.add_action(UNIT, st._sent[i].ent_type)
                    self.add_action(LAST, st._sent[i].ent_type)


cdef class Missing:
    @staticmethod
    cdef bint is_valid(const StateC* st, int label) nogil:
        return False

    @staticmethod
    cdef int transition(StateC* s, int label) nogil:
        pass

    @staticmethod
    cdef weight_t cost(StateClass s, const GoldParseC* gold, int label) nogil:
        return 9000


cdef class Begin:
    @staticmethod
    cdef bint is_valid(const StateC* st, int label) nogil:
        # Ensure we don't clobber preset entities. If no entity preset,
        # ent_iob is 0
        cdef int preset_ent_iob = st.B_(0).ent_iob
        if preset_ent_iob == 1:
            return False
        elif preset_ent_iob == 2:
            return False
        elif preset_ent_iob == 3 and st.B_(0).ent_type != label:
            return False
        # If the next word is B or O, we can't B now
        elif st.B_(1).ent_iob == 2 or st.B_(1).ent_iob == 3:
            return False
        # If the current word is B, and the next word isn't I, the current word
        # is really U
        elif preset_ent_iob == 3 and st.B_(1).ent_iob != 1:
            return False
        # Don't allow entities to extend across sentence boundaries
        elif st.B_(1).sent_start:
            return False
        else:
            return label != 0 and not st.entity_is_open()

    @staticmethod
    cdef int transition(StateC* st, int label) nogil:
        st.open_ent(label)
        st.set_ent_tag(st.B(0), 3, label)
        st.push()
        st.pop()

    @staticmethod
    cdef weight_t cost(StateClass s, const GoldParseC* gold, int label) nogil:
        cdef int g_act = gold.ner[s.B(0)].move
        cdef int g_tag = gold.ner[s.B(0)].label

        if g_act == MISSING:
            return 0
        elif g_act == BEGIN:
            # B, Gold B --> Label match
            return label != g_tag
        else:
            # B, Gold I --> False (P)
            # B, Gold L --> False (P)
            # B, Gold O --> False (P)
            # B, Gold U --> False (P)
            return 1


cdef class In:
    @staticmethod
    cdef bint is_valid(const StateC* st, int label) nogil:
        cdef int preset_ent_iob = st.B_(0).ent_iob
        if preset_ent_iob == 2:
            return False
        elif preset_ent_iob == 3:
            return False
        # TODO: Is this quite right?
        # I think it's supposed to be ensuring the gazetteer matches are maintained
        elif st.B_(1).ent_iob != preset_ent_iob:
            return False
        # Don't allow entities to extend across sentence boundaries
        elif st.B_(1).sent_start:
            return False
        return st.entity_is_open() and label != 0 and st.E_(0).ent_type == label
    
    @staticmethod
    cdef int transition(StateC* st, int label) nogil:
        st.set_ent_tag(st.B(0), 1, label)
        st.push()
        st.pop()

    @staticmethod
    cdef weight_t cost(StateClass s, const GoldParseC* gold, int label) nogil:
        move = IN
        cdef int next_act = gold.ner[s.B(1)].move if s.B(0) < s.c.length else OUT
        cdef int g_act = gold.ner[s.B(0)].move
        cdef int g_tag = gold.ner[s.B(0)].label
        cdef bint is_sunk = _entity_is_sunk(s, gold.ner)
        
        if g_act == MISSING:
            return 0
        elif g_act == BEGIN:
            # I, Gold B --> True (P of bad open entity sunk, R of this entity sunk)
            return 0
        elif g_act == IN:
            # I, Gold I --> True (label forced by prev, if mismatch, P and R both sunk)
            return 0
        elif g_act == LAST:
            # I, Gold L --> True iff this entity sunk and next tag == O
            return not (is_sunk and (next_act == OUT or next_act == MISSING))
        elif g_act == OUT:
            # I, Gold O --> True iff next tag == O
            return not (next_act == OUT or next_act == MISSING)
        elif g_act == UNIT:
            # I, Gold U --> True iff next tag == O
            return next_act != OUT
        else:
            return 1


cdef class Last:
    @staticmethod
    cdef bint is_valid(const StateC* st, int label) nogil:
        if st.B_(1).ent_iob == 1:
            return False
        return st.entity_is_open() and label != 0 and st.E_(0).ent_type == label

    @staticmethod
    cdef int transition(StateC* st, int label) nogil:
        st.close_ent()
        st.set_ent_tag(st.B(0), 1, label)
        st.push()
        st.pop()

    @staticmethod
    cdef weight_t cost(StateClass s, const GoldParseC* gold, int label) nogil:
        move = LAST

        cdef int g_act = gold.ner[s.B(0)].move
        cdef int g_tag = gold.ner[s.B(0)].label
        
        if g_act == MISSING:
            return 0
        elif g_act == BEGIN:
            # L, Gold B --> True
            return 0
        elif g_act == IN:
            # L, Gold I --> True iff this entity sunk
            return not _entity_is_sunk(s, gold.ner)
        elif g_act == LAST:
            # L, Gold L --> True
            return 0
        elif g_act == OUT:
            # L, Gold O --> True
            return 0
        elif g_act == UNIT:
            # L, Gold U --> True
            return 0
        else:
            return 1


cdef class Unit:
    @staticmethod
    cdef bint is_valid(const StateC* st, int label) nogil:
        cdef int preset_ent_iob = st.B_(0).ent_iob
        if preset_ent_iob == 2:
            return False
        elif preset_ent_iob == 1:
            return False
        elif preset_ent_iob == 3 and st.B_(0).ent_type != label:
            return False
        elif st.B_(1).ent_iob == 1:
            return False
        return label != 0 and not st.entity_is_open()

    @staticmethod
    cdef int transition(StateC* st, int label) nogil:
        st.open_ent(label)
        st.close_ent()
        st.set_ent_tag(st.B(0), 3, label)
        st.push()
        st.pop()

    @staticmethod
    cdef weight_t cost(StateClass s, const GoldParseC* gold, int label) nogil:
        cdef int g_act = gold.ner[s.B(0)].move
        cdef int g_tag = gold.ner[s.B(0)].label

        if g_act == MISSING:
            return 0
        elif g_act == UNIT:
            # U, Gold U --> True iff tag match
            return label != g_tag
        else:
            # U, Gold B --> False
            # U, Gold I --> False
            # U, Gold L --> False
            # U, Gold O --> False
            return 1


cdef class Out:
    @staticmethod
    cdef bint is_valid(const StateC* st, int label) nogil:
        cdef int preset_ent_iob = st.B_(0).ent_iob
        if preset_ent_iob == 3:
            return False
        elif preset_ent_iob == 1:
            return False
        return not st.entity_is_open()

    @staticmethod
    cdef int transition(StateC* st, int label) nogil:
        st.set_ent_tag(st.B(0), 2, 0)
        st.push()
        st.pop()
    
    @staticmethod
    cdef weight_t cost(StateClass s, const GoldParseC* gold, int label) nogil:
        cdef int g_act = gold.ner[s.B(0)].move
        cdef int g_tag = gold.ner[s.B(0)].label

        if g_act == MISSING:
            return 0
        elif g_act == BEGIN:
            # O, Gold B --> False
            return 1
        elif g_act == IN:
            # O, Gold I --> True
            return 0
        elif g_act == LAST:
            # O, Gold L --> True
            return 0
        elif g_act == OUT:
            # O, Gold O --> True
            return 0
        elif g_act == UNIT:
            # O, Gold U --> False
            return 1
        else:
            return 1
    

class OracleError(Exception):
    pass


class UnknownMove(Exception):
    pass
