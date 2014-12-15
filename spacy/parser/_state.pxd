from cymem.cymem cimport Pool


cdef struct Subtree:
    int[5] kids
    int[5] labels
    int length


cdef struct State:
    double score
    size_t i
    size_t n
    size_t stack_len
    size_t top

    size_t* stack
    
    Subtree* lefts
    Subtree* rights
    int* heads
    int* labels


cdef int add_dep(const State *s, size_t head, size_t child, size_t label) except -1

cdef size_t pop_stack(State *s) except 0
cdef int push_stack(State *s) except -1


cdef inline size_t get_s1(const State *s) nogil:
    if s.stack_len < 2:
        return 0
    return s.stack[s.stack_len - 2]


cdef inline size_t get_l(const State *s, size_t head) nogil:
    cdef const Subtree* subtree = &s.lefts[head]
    if subtree.length == 0:
        return 0
    return subtree.kids[subtree.length - 1]


cdef inline size_t get_l2(const State *s, size_t head) nogil:
    cdef const Subtree* subtree = &s.lefts[head]
    if subtree.length < 2:
        return 0
    return subtree.kids[subtree.length - 2]


cdef inline size_t get_r(const State *s, size_t head) nogil:
    cdef const Subtree* subtree = &s.rights[head]
    if subtree.length == 0:
        return 0
    return subtree.kids[subtree.length - 1]


cdef inline size_t get_r2(const State *s, size_t head) nogil:
    cdef const Subtree* subtree = &s.rights[head]
    if subtree.length < 2:
        return 0
    return subtree.kids[subtree.length - 2]


cdef inline bint at_eol(const State *s) nogil:
    return s.i >= (s.n - 1)


cdef inline bint is_final(State *s) nogil:
    return at_eol(s) and s.stack_len == 0


cdef int has_child_in_buffer(State *s, size_t word, int* gold) except -1
cdef int has_head_in_buffer(State *s, size_t word, int* gold) except -1
cdef int has_child_in_stack(State *s, size_t word, int* gold) except -1
cdef int has_head_in_stack(State *s, size_t word, int* gold) except -1

cdef State* init_state(Pool mem, const int sent_length) except NULL
