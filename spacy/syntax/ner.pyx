# coding: utf-8
from __future__ import unicode_literals

from thinc.typedefs cimport weight_t
from thinc.extra.search cimport Beam
from collections import OrderedDict

from .stateclass cimport StateClass
from ._state cimport StateC
from .transition_system cimport Transition
from .transition_system cimport do_func_t
from ..gold cimport GoldParseC, GoldParse
from ..errors import Errors


cdef enum:
    MISSING
    BEGIN
    IN
    LAST
    UNIT
    OUT
    ISNT
    N_MOVES


MOVE_NAMES = [None] * N_MOVES
MOVE_NAMES[MISSING] = 'M'
MOVE_NAMES[BEGIN] = 'B'
MOVE_NAMES[IN] = 'I'
MOVE_NAMES[LAST] = 'L'
MOVE_NAMES[UNIT] = 'U'
MOVE_NAMES[OUT] = 'O'
MOVE_NAMES[ISNT] = 'x'


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
    def __init__(self, *args, **kwargs):
        TransitionSystem.__init__(self, *args, **kwargs)

    def __reduce__(self):
        labels_by_action = OrderedDict()
        cdef Transition t
        for trans in self.c[:self.n_moves]:
            label_str = self.strings[trans.label]
            labels_by_action.setdefault(trans.move, []).append(label_str)
        return (BiluoPushDown, (self.strings, labels_by_action),
                None, None)

    @classmethod
    def get_actions(cls, **kwargs):
        actions = kwargs.get('actions', OrderedDict((
            (MISSING, ['']),
            (BEGIN, []),
            (IN, []),
            (LAST, []),
            (UNIT, []),
            (OUT, [''])
        )))
        seen_entities = set()
        for entity_type in kwargs.get('entity_types', []):
            if entity_type in seen_entities:
                continue
            seen_entities.add(entity_type)
            for action in (BEGIN, IN, LAST, UNIT):
                actions[action].append(entity_type)
        moves = ('M', 'B', 'I', 'L', 'U')
        for raw_text, sents in kwargs.get('gold_parses', []):
            for (ids, words, tags, heads, labels, biluo), _ in sents:
                for i, ner_tag in enumerate(biluo):
                    if ner_tag != 'O' and ner_tag != '-':
                        _, label = ner_tag.split('-', 1)
                        if label not in seen_entities:
                            seen_entities.add(label)
                            for move_str in ('B', 'I', 'L', 'U'):
                                actions[moves.index(move_str)].append(label)
        return actions

    property action_types:
        def __get__(self):
            return (BEGIN, IN, LAST, UNIT, OUT)

    def move_name(self, int move, attr_t label):
        if move == OUT:
            return 'O'
        elif move == MISSING:
            return 'M'
        else:
            return MOVE_NAMES[move] + '-' + self.strings[label]

    def has_gold(self, GoldParse gold, start=0, end=None):
        end = end or len(gold.ner)
        if all([tag in ('-', None) for tag in gold.ner[start:end]]):
            return False
        else:
            return True

    def preprocess_gold(self, GoldParse gold):
        if not self.has_gold(gold):
            return None
        for i in range(gold.length):
            gold.c.ner[i] = self.lookup_transition(gold.ner[i])
        return gold

    def get_beam_annot(self, Beam beam):
        entities = {}
        probs = beam.probs
        for i in range(beam.size):
            state = <StateC*>beam.at(i)
            if state.is_final():
                self.finalize_state(state)
                prob = probs[i]
                for j in range(state._e_i):
                    start = state._ents[j].start
                    end = state._ents[j].end
                    label = state._ents[j].label
                    entities.setdefault((start, end, label), 0.0)
                    entities[(start, end, label)] += prob
        return entities

    def get_beam_parses(self, Beam beam):
        parses = []
        probs = beam.probs
        for i in range(beam.size):
            state = <StateC*>beam.at(i)
            if state.is_final():
                self.finalize_state(state)
                prob = probs[i]
                parse = []
                for j in range(state._e_i):
                    start = state._ents[j].start
                    end = state._ents[j].end
                    label = state._ents[j].label
                    parse.append((start, end, self.strings[label]))
                parses.append((prob, parse))
        return parses

    cdef Transition lookup_transition(self, object name) except *:
        cdef attr_t label
        if name == '-' or name is None:
            return Transition(clas=0, move=MISSING, label=0, score=0)
        elif name == '!O':
            return Transition(clas=0, move=ISNT, label=0, score=0)
        elif '-' in name:
            move_str, label_str = name.split('-', 1)
            # Hacky way to denote 'not this entity'
            if label_str.startswith('!'):
                label_str = label_str[1:]
                move_str = 'x'
            label = self.strings.add(label_str)
        else:
            move_str = name
            label = 0
        move = MOVE_NAMES.index(move_str)
        if move == ISNT:
            return Transition(clas=0, move=ISNT, label=label, score=0)
        for i in range(self.n_moves):
            if self.c[i].move == move and self.c[i].label == label:
                return self.c[i]
        else:
            raise KeyError(Errors.E022.format(name=name))

    cdef Transition init_transition(self, int clas, int move, attr_t label) except *:
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
            raise ValueError(Errors.E019.format(action=move, src='ner'))
        return t

    def add_action(self, int action, label_name):
        cdef attr_t label_id
        if not isinstance(label_name, (int, long)):
            label_id = self.strings.add(label_name)
        else:
            label_id = label_name
        if action == OUT and label_id != 0:
            return
        if action == MISSING or action == ISNT:
            return
        # Check we're not creating a move we already have, so that this is
        # idempotent
        for trans in self.c[:self.n_moves]:
            if trans.move == action and trans.label == label_id:
                return 0
        if self.n_moves >= self._size:
            self._size *= 2
            self.c = <Transition*>self.mem.realloc(self.c, self._size * sizeof(self.c[0]))
        self.c[self.n_moves] = self.init_transition(self.n_moves, action, label_id)
        self.n_moves += 1
        return 1

    cdef int initialize_state(self, StateC* st) nogil:
        # This is especially necessary when we use limited training data.
        for i in range(st.length):
            if st._sent[i].ent_type != 0:
                with gil:
                    self.add_action(BEGIN, st._sent[i].ent_type)
                    self.add_action(IN, st._sent[i].ent_type)
                    self.add_action(UNIT, st._sent[i].ent_type)
                    self.add_action(LAST, st._sent[i].ent_type)


cdef class Missing:
    @staticmethod
    cdef bint is_valid(const StateC* st, attr_t label) nogil:
        return False

    @staticmethod
    cdef int transition(StateC* s, attr_t label) nogil:
        pass

    @staticmethod
    cdef weight_t cost(StateClass s, const GoldParseC* gold, attr_t label) nogil:
        return 9000


cdef class Begin:
    @staticmethod
    cdef bint is_valid(const StateC* st, attr_t label) nogil:
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
        elif st.B_(1).sent_start == 1:
            return False
        else:
            return label != 0 and not st.entity_is_open()

    @staticmethod
    cdef int transition(StateC* st, attr_t label) nogil:
        st.open_ent(label)
        st.set_ent_tag(st.B(0), 3, label)
        st.push()
        st.pop()

    @staticmethod
    cdef weight_t cost(StateClass s, const GoldParseC* gold, attr_t label) nogil:
        cdef int g_act = gold.ner[s.B(0)].move
        cdef attr_t g_tag = gold.ner[s.B(0)].label

        if g_act == MISSING:
            return 0
        elif g_act == BEGIN:
            # B, Gold B --> Label match
            return label != g_tag
        # Support partial supervision in the form of "not this label"
        elif g_act == ISNT:
            return label == g_tag
        else:
            # B, Gold I --> False (P)
            # B, Gold L --> False (P)
            # B, Gold O --> False (P)
            # B, Gold U --> False (P)
            return 1


cdef class In:
    @staticmethod
    cdef bint is_valid(const StateC* st, attr_t label) nogil:
        cdef int preset_ent_iob = st.B_(0).ent_iob
        if preset_ent_iob == 2:
            return False
        elif preset_ent_iob == 3:
            return False
        # TODO: Is this quite right? I think it's supposed to be ensuring the
        # gazetteer matches are maintained
        elif st.B_(1).ent_iob != preset_ent_iob:
            return False
        # Don't allow entities to extend across sentence boundaries
        elif st.B_(1).sent_start == 1:
            return False
        return st.entity_is_open() and label != 0 and st.E_(0).ent_type == label

    @staticmethod
    cdef int transition(StateC* st, attr_t label) nogil:
        st.set_ent_tag(st.B(0), 1, label)
        st.push()
        st.pop()

    @staticmethod
    cdef weight_t cost(StateClass s, const GoldParseC* gold, attr_t label) nogil:
        move = IN
        cdef int next_act = gold.ner[s.B(1)].move if s.B(0) < s.c.length else OUT
        cdef int g_act = gold.ner[s.B(0)].move
        cdef attr_t g_tag = gold.ner[s.B(0)].label
        cdef bint is_sunk = _entity_is_sunk(s, gold.ner)

        if g_act == MISSING:
            return 0
        elif g_act == BEGIN:
            # I, Gold B --> True
            # (P of bad open entity sunk, R of this entity sunk)
            return 0
        elif g_act == IN:
            # I, Gold I --> True
            # (label forced by prev, if mismatch, P and R both sunk)
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
        # Support partial supervision in the form of "not this label"
        elif g_act == ISNT:
            return 0
        else:
            return 1


cdef class Last:
    @staticmethod
    cdef bint is_valid(const StateC* st, attr_t label) nogil:
        if st.B_(1).ent_iob == 1:
            return False
        return st.entity_is_open() and label != 0 and st.E_(0).ent_type == label

    @staticmethod
    cdef int transition(StateC* st, attr_t label) nogil:
        st.close_ent()
        st.set_ent_tag(st.B(0), 1, label)
        st.push()
        st.pop()

    @staticmethod
    cdef weight_t cost(StateClass s, const GoldParseC* gold, attr_t label) nogil:
        move = LAST

        cdef int g_act = gold.ner[s.B(0)].move
        cdef attr_t g_tag = gold.ner[s.B(0)].label

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
        # Support partial supervision in the form of "not this label"
        elif g_act == ISNT:
            return 0
        else:
            return 1


cdef class Unit:
    @staticmethod
    cdef bint is_valid(const StateC* st, attr_t label) nogil:
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
    cdef int transition(StateC* st, attr_t label) nogil:
        st.open_ent(label)
        st.close_ent()
        st.set_ent_tag(st.B(0), 3, label)
        st.push()
        st.pop()

    @staticmethod
    cdef weight_t cost(StateClass s, const GoldParseC* gold, attr_t label) nogil:
        cdef int g_act = gold.ner[s.B(0)].move
        cdef attr_t g_tag = gold.ner[s.B(0)].label

        if g_act == MISSING:
            return 0
        elif g_act == UNIT:
            # U, Gold U --> True iff tag match
            return label != g_tag
        # Support partial supervision in the form of "not this label"
        elif g_act == ISNT:
            return label == g_tag
        else:
            # U, Gold B --> False
            # U, Gold I --> False
            # U, Gold L --> False
            # U, Gold O --> False
            return 1


cdef class Out:
    @staticmethod
    cdef bint is_valid(const StateC* st, attr_t label) nogil:
        cdef int preset_ent_iob = st.B_(0).ent_iob
        if preset_ent_iob == 3:
            return False
        elif preset_ent_iob == 1:
            return False
        return not st.entity_is_open()

    @staticmethod
    cdef int transition(StateC* st, attr_t label) nogil:
        st.set_ent_tag(st.B(0), 2, 0)
        st.push()
        st.pop()

    @staticmethod
    cdef weight_t cost(StateClass s, const GoldParseC* gold, attr_t label) nogil:
        cdef int g_act = gold.ner[s.B(0)].move
        cdef attr_t g_tag = gold.ner[s.B(0)].label

        if g_act == ISNT and g_tag == 0:
            return 1
        elif g_act == MISSING or g_act == ISNT:
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
