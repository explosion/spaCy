from .moves cimport BEGIN, UNIT


cdef int begin_entity(State* s, label) except -1:
    s.curr.start = s.i
    s.curr.label = label


cdef int end_entity(State* s) except -1:
    s.curr.end = s.i + 1
    s.ents[s.j] = s.curr
    s.j += 1
    s.curr.start = 0
    s.curr.label = -1
    s.curr.end = 0


cdef State* init_state(Pool mem, int sent_length) except NULL:
    s = <State*>mem.alloc(1, sizeof(State))
    s.j = 0
    s.ents = <Entity*>mem.alloc(sent_length, sizeof(Entity))
    for i in range(sent_length):
        s.ents[i].label = -1
    s.curr.label = -1
    s.tags = <int*>mem.alloc(sent_length, sizeof(int))
    s.length = sent_length
    return s


cdef bint entity_is_open(State *s) except -1:
    return s.curr.label != -1


cdef bint entity_is_sunk(State *s, Move* golds) except -1:
    if not entity_is_open(s):
        return False

    cdef Move* gold = &golds[s.curr.start]
    if gold.action != BEGIN and gold.action != UNIT:
        return True
    elif gold.label != s.curr.label:
        return True
    else:
        return False
