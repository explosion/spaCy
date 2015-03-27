from libc.string cimport memmove, memcpy
from cymem.cymem cimport Pool

from ..lexeme cimport EMPTY_LEXEME
from ..structs cimport TokenC, Entity


DEF PADDING = 5
DEF NON_MONOTONIC = True


cdef int add_dep(State *s, int head, int child, int label) except -1:
    cdef int dist = head - child
    s.sent[child].head = dist
    s.sent[child].dep = label
    # Keep a bit-vector tracking child dependencies.  If a word has a child at
    # offset i from it, set that bit (tracking left and right separately)
    if child > head:
        s.sent[head].r_kids |= 1 << (-dist)
    else:
        s.sent[head].l_kids |= 1 << dist


cdef int pop_stack(State *s) except -1:
    assert s.stack_len >= 1
    s.stack_len -= 1
    s.stack -= 1
    if s.stack_len == 0 and not at_eol(s):
        push_stack(s)
        

cdef int push_stack(State *s) except -1:
    assert s.i < s.sent_len
    s.stack += 1
    s.stack[0] = s.i
    s.stack_len += 1
    s.i += 1


cdef int children_in_buffer(const State *s, int head, const int* gold) except -1:
    # Golds holds an array of head offsets --- the head of word i is i - golds[i]
    # Iterate over the tokens of the queue, and check whether their gold head is
    # our target
    cdef int i
    cdef int n = 0
    for i in range(s.i, s.sent_len):
        if gold[i] == head:
            n += 1
    return n


cdef int head_in_buffer(const State *s, const int child, const int* gold) except -1:
    return gold[child] >= s.i


cdef int children_in_stack(const State *s, const int head, const int* gold) except -1:
    cdef int i
    cdef int n = 0
    for i in range(s.stack_len):
        if gold[s.stack[-i]] == head:
            if NON_MONOTONIC or not has_head(get_s0(s)):
                n += 1
    return n


cdef int head_in_stack(const State *s, const int child, const int* gold) except -1:
    cdef int i
    for i in range(s.stack_len):
        if gold[child] == s.stack[-i]:
            return 1
    return 0


cdef const TokenC* get_left(const State* s, const TokenC* head, const int idx) nogil:
    cdef uint32_t kids = head.l_kids
    if kids == 0:
        return NULL
    cdef int offset = _nth_significant_bit(kids, idx)
    cdef const TokenC* child = head - offset
    if child >= s.sent:
        return child
    else:
        return NULL


cdef const TokenC* get_right(const State* s, const TokenC* head, const int idx) nogil:
    cdef uint32_t kids = head.r_kids
    if kids == 0:
        return NULL
    cdef int offset = _nth_significant_bit(kids, idx)
    cdef const TokenC* child = head + offset
    if child < (s.sent + s.sent_len):
        return child
    else:
        return NULL


cdef bint has_head(const TokenC* t) nogil:
    return t.head != 0


cdef int count_left_kids(const TokenC* head) nogil:
    return _popcount(head.l_kids)


cdef int count_right_kids(const TokenC* head) nogil:
    return _popcount(head.r_kids)


cdef State* new_state(Pool mem, const TokenC* sent, const int sent_len) except NULL:
    cdef int padded_len = sent_len + PADDING + PADDING
    cdef State* s = <State*>mem.alloc(1, sizeof(State))
    s.ent = <Entity*>mem.alloc(padded_len, sizeof(Entity))
    s.stack = <int*>mem.alloc(padded_len, sizeof(int))
    for i in range(PADDING):
        s.stack[i] = -1
    s.stack += (PADDING - 1)
    s.ent += (PADDING - 1)
    assert s.stack[0] == -1
    state_sent = <TokenC*>mem.alloc(padded_len, sizeof(TokenC))
    memcpy(state_sent, sent - PADDING, padded_len * sizeof(TokenC))
    s.sent = state_sent + PADDING
    s.stack_len = 0
    s.i = 0
    s.sent_len = sent_len
    return s
