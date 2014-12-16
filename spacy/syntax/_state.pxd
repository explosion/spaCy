from libc.stdint cimport uint32_t

from cymem.cymem cimport Pool

from ..tokens cimport TokenC


cdef struct State:
    TokenC* sent
    int i
    int sent_len
    int stack_len


cdef int add_dep(State *s, TokenC* head, TokenC* child, int label) except -1


cdef TokenC* pop_stack(State *s) except NULL
cdef int push_stack(State *s) except -1


cdef inline bint has_head(const TokenC* t) nogil:
    return t.head != 0


cdef inline int get_idx(const State* s, const TokenC* t) nogil:
    return t - s.sent


cdef inline TokenC* get_n0(const State* s) nogil:
    return &s.sent[s.i]


cdef inline TokenC* get_n1(const State* s) nogil:
    if s.i < (s.sent_len - 1):
        return &s.sent[s.i+1]
    else:
        return s.sent - 1


cdef inline TokenC* get_n2(const State* s) nogil:
    return &s.sent[s.i+2]


cdef inline TokenC* get_s0(const State *s) nogil:
    return s.stack[0]


cdef inline TokenC* get_s1(const State *s) nogil:
    # Rely on our padding to ensure we don't go out of bounds here
    cdef TokenC** s1 = s.stack - 1
    return s1[0]


cdef inline TokenC* get_s2(const State *s) nogil:
    # Rely on our padding to ensure we don't go out of bounds here
    cdef TokenC** s2 = s.stack - 2
    return s2[0]

cdef TokenC* get_right(State* s, TokenC* head, int idx) nogil
cdef TokenC* get_left(State* s, TokenC* head, int idx) nogil

cdef inline bint at_eol(const State *s) nogil:
    return s.i >= s.sent_len


cdef inline bint is_final(const State *s) nogil:
    return at_eol(s) # The stack will be attached to root anyway


cdef int children_in_buffer(const State *s, const TokenC* target, list gold) except -1
cdef int head_in_buffer(const State *s, const TokenC* target, list gold) except -1
cdef int children_in_stack(const State *s, const TokenC* target, list gold) except -1
cdef int head_in_stack(const State *s, const TokenC*, list gold) except -1

cdef State* init_state(Pool mem, TokenC* sent, const int sent_length) except NULL



cdef inline uint32_t _nth_significant_bit(uint32_t bits, int n) nogil:
    cdef int i
    for i in range(32):
        if bits & (1 << i):
            return i
    return 0
