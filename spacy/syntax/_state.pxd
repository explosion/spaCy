from libc.stdint cimport uint32_t

from cymem.cymem cimport Pool

from ..tokens cimport TokenC


cdef struct State:
    TokenC* sent
    int* stack
    int i
    int sent_len
    int stack_len


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
    return at_eol(s) # The stack will be attached to root anyway


cdef int children_in_buffer(const State *s, const int head, int* gold) except -1
cdef int head_in_buffer(const State *s, const int child, int* gold) except -1
cdef int children_in_stack(const State *s, const int head, int* gold) except -1
cdef int head_in_stack(const State *s, const int child, int* gold) except -1

cdef State* init_state(Pool mem, TokenC* sent, const int sent_length) except NULL


cdef int count_left_kids(const TokenC* head) nogil


cdef int count_right_kids(const TokenC* head) nogil


# From https://en.wikipedia.org/wiki/Hamming_weight
cdef inline uint32_t _popcount(uint32_t x) nogil:
    """Find number of non-zero bits."""
    cdef int count = 0
    while x != 0:
        x &= x - 1
        count += 1
    return count


cdef inline uint32_t _nth_significant_bit(uint32_t bits, int n) nogil:
    cdef int i
    for i in range(32):
        if bits & (1 << i):
            n -= 1
            if n < 1:
                return i
    return 0
