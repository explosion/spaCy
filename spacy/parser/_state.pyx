# cython: profile=True
from libc.string cimport memmove
from cymem.cymem cimport Pool


cdef int add_dep(State *s, size_t head, size_t child, size_t label) except -1:
    s.heads[child] = head
    s.labels[child] = label
    cdef Subtree* subtree = &s.lefts[head] if child < head else &s.rights[head]
    if subtree.length == 5:
        memmove(subtree.kids, &subtree.kids[1], 4 * sizeof(int))
        memmove(subtree.labels, &subtree.labels[1], 4 * sizeof(int))
        subtree.kids[4] = child
        subtree.labels[4] = label
    else:
        subtree.kids[subtree.length - 1] = child
        subtree.kids[subtree.length - 1] = label
        subtree.length += 1


cdef size_t pop_stack(State *s) except 0:
    cdef size_t popped
    assert s.stack_len >= 1
    popped = s.top
    s.top = get_s1(s)
    s.stack_len -= 1
    assert s.top <= s.n, s.top
    assert popped != 0
    return popped


cdef int push_stack(State *s) except -1:
    s.top = s.i
    s.stack[s.stack_len] = s.i
    s.stack_len += 1
    assert s.top <= s.n
    s.i += 1


cdef int has_child_in_buffer(State *s, size_t word, int* gold_heads) except -1:
    assert word != 0
    cdef size_t buff_i
    cdef int n = 0
    for buff_i in range(s.i, s.n):
        if s.heads[buff_i] == 0 and gold_heads[buff_i] == word:
            n += 1
    return n


cdef int has_head_in_buffer(State *s, size_t word, int* gold_heads) except -1:
    assert word != 0
    cdef size_t buff_i
    for buff_i in range(s.i, s.n):
        if s.heads[buff_i] == 0 and gold_heads[word] == buff_i:
            return 1
    return 0


cdef int has_child_in_stack(State *s, size_t word, int* gold_heads) except -1:
    assert word != 0
    cdef size_t i, stack_i
    cdef int n = 0
    for i in range(s.stack_len):
        stack_i = s.stack[i]
        # Should this be sensitive to whether the word has a head already?
        if gold_heads[stack_i] == word:
            n += 1
    return n


cdef int has_head_in_stack(State *s, size_t word, int* gold_heads) except -1:
    assert word != 0
    cdef size_t i, stack_i
    for i in range(s.stack_len):
        stack_i = s.stack[i]
        if gold_heads[word] == stack_i:
            return 1
    return 0


DEF PADDING = 5


cdef State* init_state(Pool mem, const int sent_length) except NULL:
    cdef size_t i
    cdef State* s = <State*>mem.alloc(1, sizeof(State))
    s.n = sent_length
    s.i = 1
    s.top = 0
    s.stack_len = 0
    n = s.n + PADDING
    s.stack = <size_t*>mem.alloc(n, sizeof(size_t))
    s.heads = <int*>mem.alloc(n, sizeof(int))
    s.labels = <int*>mem.alloc(n, sizeof(int))
    s.lefts = <Subtree*>mem.alloc(n, sizeof(Subtree))
    s.rights = <Subtree*>mem.alloc(n, sizeof(Subtree))
    return s
