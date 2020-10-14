from libc.stdint cimport int32_t
from cymem.cymem cimport Pool

from collections import Counter

from ...typedefs cimport weight_t, attr_t
from ...lexeme cimport Lexeme
from ...attrs cimport IS_SPACE
from ...training.example cimport Example
from .stateclass cimport StateClass
from ._state cimport StateC
from .transition_system cimport Transition, do_func_t

from ...errors import Errors


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


cdef struct GoldNERStateC:
    Transition* ner
    int32_t length


cdef class BiluoGold:
    cdef Pool mem
    cdef GoldNERStateC c

    def __init__(self, BiluoPushDown moves, StateClass stcls, Example example):
        self.mem = Pool()
        self.c = create_gold_state(self.mem, moves, stcls, example)

    def update(self, StateClass stcls):
        update_gold_state(&self.c, stcls)



cdef GoldNERStateC create_gold_state(
    Pool mem,
    BiluoPushDown moves,
    StateClass stcls,
    Example example
) except *:
    cdef GoldNERStateC gs
    gs.ner = <Transition*>mem.alloc(example.x.length, sizeof(Transition))
    ner_tags = example.get_aligned_ner()
    for i, ner_tag in enumerate(ner_tags):
        gs.ner[i] = moves.lookup_transition(ner_tag)
    return gs


cdef void update_gold_state(GoldNERStateC* gs, StateClass stcls) except *:
    # We don't need to update each time, unlike the parser.
    pass


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

    @classmethod
    def get_actions(cls, **kwargs):
        actions = {
            MISSING: Counter(),
            BEGIN: Counter(),
            IN: Counter(),
            LAST: Counter(),
            UNIT: Counter(),
            OUT: Counter()
        }
        actions[OUT][''] = 1  # Represents a token predicted to be outside of any entity
        actions[UNIT][''] = 1 # Represents a token prohibited to be in an entity
        for entity_type in kwargs.get('entity_types', []):
            for action in (BEGIN, IN, LAST, UNIT):
                actions[action][entity_type] = 1
        moves = ('M', 'B', 'I', 'L', 'U')
        for example in kwargs.get('examples', []):
            for token in example.y:
                ent_type = token.ent_type_
                if ent_type:
                    for action in (BEGIN, IN, LAST, UNIT):
                        actions[action][ent_type] += 1
        return actions

    @property
    def action_types(self):
        return (BEGIN, IN, LAST, UNIT, OUT)

    def move_name(self, int move, attr_t label):
        if move == OUT:
            return 'O'
        elif move == MISSING:
            return 'M'
        else:
            return MOVE_NAMES[move] + '-' + self.strings[label]

    def init_gold_batch(self, examples):
        all_states = self.init_batch([eg.predicted for eg in examples])
        golds = []
        states = []
        for state, eg in zip(all_states, examples):
            if self.has_gold(eg) and not state.is_final():
                golds.append(self.init_gold(state, eg))
                states.append(state)
        n_steps = sum([len(s.queue) for s in states])
        return states, golds, n_steps

    cdef Transition lookup_transition(self, object name) except *:
        cdef attr_t label
        if name == '-' or name == '' or name is None:
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

    def add_action(self, int action, label_name, freq=None):
        cdef attr_t label_id
        if not isinstance(label_name, (int, long)):
            label_id = self.strings.add(label_name)
        else:
            label_id = label_name
        if action == OUT and label_id != 0:
            return None
        if action == MISSING or action == ISNT:
            return None
        # Check we're not creating a move we already have, so that this is
        # idempotent
        for trans in self.c[:self.n_moves]:
            if trans.move == action and trans.label == label_id:
                return 0
        if self.n_moves >= self._size:
            self._size = self.n_moves
            self._size *= 2
            self.c = <Transition*>self.mem.realloc(self.c, self._size * sizeof(self.c[0]))
        self.c[self.n_moves] = self.init_transition(self.n_moves, action, label_id)
        self.n_moves += 1
        if self.labels.get(action, []):
            freq = min(0, min(self.labels[action].values()))
            self.labels[action][label_name] = freq-1
        else:
            self.labels[action] = Counter()
            self.labels[action][label_name] = -1
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

    def init_gold(self, StateClass state, Example example):
        return BiluoGold(self, state, example)

    def has_gold(self, Example eg, start=0, end=None):
        for word in eg.y[start:end]:
            if word.ent_iob != 0:
                return True
        else:
            return False

    def get_cost(self, StateClass stcls, gold, int i):
        if not isinstance(gold, BiluoGold):
            raise TypeError(Errors.E909.format(name="BiluoGold"))
        cdef BiluoGold gold_ = gold
        gold_state = gold_.c
        n_gold = 0
        if self.c[i].is_valid(stcls.c, self.c[i].label):
            cost = self.c[i].get_cost(stcls, &gold_state, self.c[i].label)
        else:
            cost = 9000
        return cost

    cdef int set_costs(self, int* is_valid, weight_t* costs,
                       StateClass stcls, gold) except -1:
        if not isinstance(gold, BiluoGold):
            raise TypeError(Errors.E909.format(name="BiluoGold"))
        cdef BiluoGold gold_ = gold
        gold_.update(stcls)
        gold_state = gold_.c
        n_gold = 0
        for i in range(self.n_moves):
            if self.c[i].is_valid(stcls.c, self.c[i].label):
                is_valid[i] = 1
                costs[i] = self.c[i].get_cost(stcls, &gold_state, self.c[i].label)
                n_gold += costs[i] <= 0
            else:
                is_valid[i] = 0
                costs[i] = 9000
        if n_gold < 1:
            raise ValueError


cdef class Missing:
    @staticmethod
    cdef bint is_valid(const StateC* st, attr_t label) nogil:
        return False

    @staticmethod
    cdef int transition(StateC* s, attr_t label) nogil:
        pass

    @staticmethod
    cdef weight_t cost(StateClass s, const void* _gold, attr_t label) nogil:
        return 9000


cdef class Begin:
    @staticmethod
    cdef bint is_valid(const StateC* st, attr_t label) nogil:
        cdef int preset_ent_iob = st.B_(0).ent_iob
        cdef attr_t preset_ent_label = st.B_(0).ent_type
        # If we're the last token of the input, we can't B -- must U or O.
        if st.B(1) == -1:
            return False
        elif st.entity_is_open():
            return False
        elif label == 0:
            return False
        elif preset_ent_iob == 1:
            # Ensure we don't clobber preset entities. If no entity preset,
            # ent_iob is 0
            return False
        elif preset_ent_iob == 3:
            # Okay, we're in a preset entity.
            if label != preset_ent_label:
                # If label isn't right, reject
                return False
            elif st.B_(1).ent_iob != 1:
                # If next token isn't marked I, we need to make U, not B.
                return False
            else:
                # Otherwise, force acceptance, even if we're across a sentence
                # boundary or the token is whitespace.
                return True
        elif st.B_(1).ent_iob == 3:
            # If the next word is B, we can't B now
            return False
        elif st.B_(1).sent_start == 1:
            # Don't allow entities to extend across sentence boundaries
            return False
        # Don't allow entities to start on whitespace
        elif Lexeme.get_struct_attr(st.B_(0).lex, IS_SPACE):
            return False
        else:
            return True

    @staticmethod
    cdef int transition(StateC* st, attr_t label) nogil:
        st.open_ent(label)
        st.set_ent_tag(st.B(0), 3, label)
        st.push()
        st.pop()

    @staticmethod
    cdef weight_t cost(StateClass s, const void* _gold, attr_t label) nogil:
        gold = <GoldNERStateC*>_gold
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
        cdef attr_t preset_ent_label = st.B_(0).ent_type
        if label == 0:
            return False
        elif st.E_(0).ent_type != label:
            return False
        elif not st.entity_is_open():
            return False
        elif st.B(1) == -1:
            # If we're at the end, we can't I.
            return False
        elif preset_ent_iob == 3:
            return False
        elif st.B_(1).ent_iob == 3:
            # If we know the next word is B, we can't be I (must be L)
            return False
        elif preset_ent_iob == 1:
            if st.B_(1).ent_iob in (0, 2):
                # if next preset is missing or O, this can't be I (must be L)
                return False
            elif label != preset_ent_label:
                # If label isn't right, reject
                return False
            else:
                # Otherwise, force acceptance, even if we're across a sentence
                # boundary or the token is whitespace.
                return True
        elif st.B(1) != -1 and st.B_(1).sent_start == 1:
            # Don't allow entities to extend across sentence boundaries
            return False
        else:
            return True

    @staticmethod
    cdef int transition(StateC* st, attr_t label) nogil:
        st.set_ent_tag(st.B(0), 1, label)
        st.push()
        st.pop()

    @staticmethod
    cdef weight_t cost(StateClass s, const void* _gold, attr_t label) nogil:
        gold = <GoldNERStateC*>_gold
        move = IN
        cdef int next_act = gold.ner[s.B(1)].move if s.B(1) >= 0 else OUT
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
        cdef int preset_ent_iob = st.B_(0).ent_iob
        cdef attr_t preset_ent_label = st.B_(0).ent_type
        if label == 0:
            return False
        elif not st.entity_is_open():
            return False
        elif preset_ent_iob == 1 and st.B_(1).ent_iob != 1:
            # If a preset entity has I followed by not-I, is L
            if label != preset_ent_label:
                # If label isn't right, reject
                return False
            else:
                # Otherwise, force acceptance, even if we're across a sentence
                # boundary or the token is whitespace.
                return True
        elif st.E_(0).ent_type != label:
            return False
        elif st.B_(1).ent_iob == 1:
            # If a preset entity has I next, we can't L here.
            return False
        else:
            return True

    @staticmethod
    cdef int transition(StateC* st, attr_t label) nogil:
        st.close_ent()
        st.set_ent_tag(st.B(0), 1, label)
        st.push()
        st.pop()

    @staticmethod
    cdef weight_t cost(StateClass s, const void* _gold, attr_t label) nogil:
        gold = <GoldNERStateC*>_gold
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
        cdef attr_t preset_ent_label = st.B_(0).ent_type
        if label == 0:
            # this is only allowed if it's a preset blocked annotation
            if preset_ent_label == 0 and preset_ent_iob == 3:
                return True
            else:
                return False
        elif st.entity_is_open():
            return False
        elif st.B_(1).ent_iob == 1:
            # If next token is In, we can't be Unit -- must be Begin
            return False
        elif preset_ent_iob == 3:
            # Okay, there's a preset entity here
            if label != preset_ent_label:
                # Require labels to match
                return False
            else:
                # Otherwise return True, ignoring the whitespace constraint.
                return True
        elif Lexeme.get_struct_attr(st.B_(0).lex, IS_SPACE):
            return False
        else:
            return True

    @staticmethod
    cdef int transition(StateC* st, attr_t label) nogil:
        st.open_ent(label)
        st.close_ent()
        st.set_ent_tag(st.B(0), 3, label)
        st.push()
        st.pop()

    @staticmethod
    cdef weight_t cost(StateClass s, const void* _gold, attr_t label) nogil:
        gold = <GoldNERStateC*>_gold
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
        if st.entity_is_open():
            return False
        elif preset_ent_iob == 3:
            return False
        elif preset_ent_iob == 1:
            return False
        else:
            return True

    @staticmethod
    cdef int transition(StateC* st, attr_t label) nogil:
        st.set_ent_tag(st.B(0), 2, 0)
        st.push()
        st.pop()

    @staticmethod
    cdef weight_t cost(StateClass s, const void* _gold, attr_t label) nogil:
        gold = <GoldNERStateC*>_gold
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
