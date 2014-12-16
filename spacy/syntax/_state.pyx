# cython: profile=True
from libc.string cimport memmove
from cymem.cymem cimport Pool

from ..lexeme cimport EMPTY_LEXEME


cdef int add_dep(State *s, TokenC* head, TokenC* child, int label) except -1:
    child.head = head - child
    child.dep_tag = label
    # Keep a bit-vector tracking child dependencies.  If a word has a child at
    # offset i from it, set that bit (tracking left and right separately)
    if child > head:
        head.r_kids |= 1 << child.head
    else:
        head.l_kids |= 1 << (-child.head)


cdef TokenC* pop_stack(State *s) except NULL:
    assert s.stack_len >= 1
    cdef TokenC* top = s.stack[0]
    s.stack -= 1
    s.stack_len -= 1
    return top


cdef int push_stack(State *s) except -1:
    assert s.i < s.sent_len
    s.stack += 1
    s.stack[0] = &s.sent[s.i]
    s.stack_len += 1
    s.i += 1


cdef int children_in_buffer(const State *s, const TokenC* target, list gold) except -1:
    # Golds holds an array of head offsets --- the head of word i is i - golds[i]
    # Iterate over the tokens of the queue, and check whether their gold head is
    # our target
    cdef int i
    cdef int n = 0
    cdef TokenC* buff_word
    cdef TokenC* buff_head
    cdef int buff_word_head_offset
    for i in range(s.i, s.sent_len):
        buff_word = &s.sent[i]
        buff_word_head_offset = gold[i]
        buff_head = buff_word + buff_word_head_offset
        if buff_head == target:
            n += 1
    return n


cdef int head_in_buffer(const State *s, const TokenC* target, list gold) except -1:
    cdef int target_idx = get_idx(s, target)
    cdef int target_head_idx = target_idx + gold[target_idx]
    return target_head_idx >= s.i


cdef int children_in_stack(const State *s, const TokenC* target, list gold) except -1:
    if s.stack_len == 0:
        return 0
    cdef int i
    cdef int n = 0
    cdef const TokenC* stack_word
    cdef const TokenC* stack_word_head
    cdef int stack_word_head_offset
    for i in range(s.stack_len):
        stack_word = (s.stack - i)[0]
        stack_word_head_offset = gold[get_idx(s, stack_word)]
        stack_word_head = (s.stack + stack_word_head_offset)[0]
        if stack_word_head == target:
            n += 1
    return n


cdef int head_in_stack(const State *s, const TokenC* target, list gold) except -1:
    if s.stack_len == 0:
        return 0
    cdef int head_offset = gold[get_idx(s, target)]
    cdef const TokenC* target_head = target + head_offset
    cdef int i
    for i in range(s.stack_len):
        if target_head == (s.stack - i)[0]:
            return 1
    return 0


cdef TokenC* get_left(State* s, TokenC* head, int idx) nogil:
    cdef uint32_t kids = head.l_kids
    if kids == 0:
        return s.sent - 1
    cdef int offset = _nth_significant_bit(kids, idx)
    cdef TokenC* child = head - offset
    if child >= s.sent:
        return child
    else:
        return s.sent - 1


cdef TokenC* get_right(State* s, TokenC* head, int idx) nogil:
    cdef uint32_t kids = head.r_kids
    if kids == 0:
        return s.sent - 1
    cdef int offset = _nth_significant_bit(kids, idx)
    cdef TokenC* child = head + offset
    if child < (s.sent + s.sent_len):
        return child
    else:
        return s.sent - 1


DEF PADDING = 5


cdef State* init_state(Pool mem, TokenC* sent, const int sent_length) except NULL:
    cdef int padded_len = sent_length + PADDING + PADDING
    cdef State* s = <State*>mem.alloc(1, sizeof(State))
    s.stack = <TokenC**>mem.alloc(padded_len, sizeof(TokenC*))
    cdef TokenC* eol_token = sent - 1
    for i in range(PADDING):
        # sent should be padded, with a suitable sentinel token here
        s.stack[0] = eol_token
        s.stack += 1
    s.stack[0] = eol_token
    s.sent = sent
    s.stack_len = 0
    s.i = 0
    s.sent_len = sent_length
    return s
