from libc.stdint cimport uint32_t

from cymem.cymem cimport Pool

from ..structs cimport TokenC, Entity, Constituent



cdef struct State:
    TokenC* sent
    int* stack
    Entity* ent
    int i
    int sent_len
    int stack_len
    int ents_len


cdef int add_dep(const State *s, const int head, const int child, const int label) except -1


cdef int pop_stack(State *s) except -1
cdef int push_stack(State *s) except -1


cdef bint has_head(const TokenC* t) nogil


cdef inline int get_idx(const State* s, const TokenC* t) nogil:
    return t - s.sent


cdef inline TokenC* get_n0(const State* s) nogil:
    return &s.sent[s.i]


cdef inline TokenC* get_n1(const State* s) nogil:
    if (s.i+1) >= s.sent_len:
        return NULL
    else:
        return &s.sent[s.i+1]


cdef inline TokenC* get_p1(const State* s) nogil:
    if s.i < 1:
        return NULL
    else:
        return &s.sent[s.i-1]


cdef inline TokenC* get_p2(const State* s) nogil:
    if s.i < 2:
        return NULL
    else:
        return &s.sent[s.i-2]


cdef inline TokenC* get_e0(const State* s) nogil:
    if s.ent.end != 0:
        return NULL
    else:
        return &s.sent[s.ent.start]


cdef inline TokenC* get_e1(const State* s) nogil:
    if s.ent.end != 0 or s.ent.start >= (s.i + 1):
        return NULL
    else:
        return &s.sent[s.ent.start + 1]


cdef inline TokenC* get_n2(const State* s) nogil:
    if (s.i + 2) >= s.sent_len:
        return NULL
    else:
        return &s.sent[s.i+2]


cdef inline TokenC* get_s0(const State *s) nogil:
    return &s.sent[s.stack[0]]


cdef inline TokenC* get_s1(const State *s) nogil:
    # Rely on our padding to ensure we don't go out of bounds here
    return &s.sent[s.stack[-1]]


cdef inline TokenC* get_s2(const State *s) nogil:
    # Rely on our padding to ensure we don't go out of bounds here
    return &s.sent[s.stack[-2]]

cdef const TokenC* get_right(const State* s, const TokenC* head, const int idx) nogil

cdef const TokenC* get_left(const State* s, const TokenC* head, const int idx) nogil

cdef inline bint at_eol(const State *s) nogil:
    return s.i >= s.sent_len


cdef inline bint is_final(const State *s) nogil:
    return at_eol(s) and s.stack_len < 2


cdef int children_in_buffer(const State *s, const int head, const int* gold) except -1
cdef int head_in_buffer(const State *s, const int child, const int* gold) except -1
cdef int children_in_stack(const State *s, const int head, const int* gold) except -1
cdef int head_in_stack(const State *s, const int child, const int* gold) except -1

cdef State* new_state(Pool mem, const TokenC* sent, const int sent_length) except NULL
cdef int copy_state(State* dest, const State* src) except -1

cdef int count_left_kids(const TokenC* head) nogil

cdef int count_right_kids(const TokenC* head) nogil
