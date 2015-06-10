from libc.string cimport memcpy, memset
from libc.stdint cimport uint32_t
from ..vocab cimport EMPTY_LEXEME
from ..structs cimport Entity


cdef class StateClass:
    def __init__(self, int length):
        cdef Pool mem = Pool()
        self._buffer = <int*>mem.alloc(length, sizeof(int))
        self._stack = <int*>mem.alloc(length, sizeof(int))
        self.shifted = <bint*>mem.alloc(length, sizeof(bint))
        self._sent = <TokenC*>mem.alloc(length, sizeof(TokenC))
        self._ents = <Entity*>mem.alloc(length, sizeof(Entity))
        self.mem = mem
        self.length = length
        self._break = length
        self._s_i = 0
        self._b_i = 0
        self._e_i = 0
        cdef int i
        for i in range(length):
            self._buffer[i] = i
        self._empty_token.lex = &EMPTY_LEXEME

    cdef int H(self, int i) nogil:
        if i < 0 or i >= self.length:
            return -1
        return self._sent[i].head + i

    cdef int E(self, int i) nogil:
        return -1

    cdef int L(self, int i, int idx) nogil:
        if idx < 1:
            return -1
        if i < 0 or i >= self.length:
            return -1
        cdef const TokenC* target = &self._sent[i]
        cdef const TokenC* ptr = self._sent

        while ptr < target:
            # If this head is still to the right of us, we can skip to it
            # No token that's between this token and this head could be our
            # child.
            if (ptr.head >= 1) and (ptr + ptr.head) < target:
                ptr += ptr.head

            elif ptr + ptr.head == target:
                idx -= 1
                if idx == 0:
                    return ptr - self._sent
                ptr += 1
            else:
                ptr += 1
        return -1

    cdef int R(self, int i, int idx) nogil:
        if idx < 1:
            return -1
        if i < 0 or i >= self.length:
            return -1
        cdef const TokenC* ptr = self._sent + (self.length - 1)
        cdef const TokenC* target = &self._sent[i]
        while ptr > target:
            # If this head is still to the right of us, we can skip to it
            # No token that's between this token and this head could be our
            # child.
            if (ptr.head < 0) and ((ptr + ptr.head) > target):
                ptr += ptr.head
            elif ptr + ptr.head == target:
                idx -= 1
                if idx == 0:
                    return ptr - self._sent
                ptr -= 1
            else:
                ptr -= 1
        return -1

    cdef const TokenC* S_(self, int i) nogil:
        return self.safe_get(self.S(i))

    cdef const TokenC* B_(self, int i) nogil:
        return self.safe_get(self.B(i))

    cdef const TokenC* H_(self, int i) nogil:
        return self.safe_get(self.H(i))

    cdef const TokenC* E_(self, int i) nogil:
        return self.safe_get(self.E(i))

    cdef const TokenC* L_(self, int i, int idx) nogil:
        return self.safe_get(self.L(i, idx))

    cdef const TokenC* R_(self, int i, int idx) nogil:
        return self.safe_get(self.R(i, idx))

    cdef const TokenC* safe_get(self, int i) nogil:
        if i < 0 or i >= self.length:
            return &self._empty_token
        else:
            return &self._sent[i]

    cdef bint empty(self) nogil:
        return self._s_i <= 0

    cdef bint eol(self) nogil:
        return self._b_i >= self._break

    cdef bint is_final(self) nogil:
        return self.stack_depth() <= 1 and self._b_i >= self.length

    cdef bint has_head(self, int i) nogil:
        return self.safe_get(i).head != 0

    cdef int n_L(self, int i) nogil:
        return _popcount(self.safe_get(i).l_kids)

    cdef int n_R(self, int i) nogil:
        return _popcount(self.safe_get(i).r_kids)

    cdef bint stack_is_connected(self) nogil:
        return False

    cdef bint entity_is_open(self) nogil:
        if self._e_i < 1:
            return False
        return self._ents[self._e_i-1].end != 0

    cdef int stack_depth(self) nogil:
        return self._s_i

    cdef int buffer_length(self) nogil:
        return self._break - self._b_i

    cdef void push(self) nogil:
        self._stack[self._s_i] = self.B(0)
        self._s_i += 1
        self._b_i += 1
        if self._b_i >= self._break:
            self._break = self.length

    cdef void pop(self) nogil:
        self._s_i -= 1

    cdef void unshift(self) nogil:
        self._b_i -= 1
        self._buffer[self._b_i] = self.S(0)
        self._s_i -= 1
        self.shifted[self.B(0)] = True

    cdef void add_arc(self, int head, int child, int label) nogil:
        if self.has_head(child):
            self.del_arc(self.H(child), child)

        cdef int dist = head - child
        self._sent[child].head = dist
        self._sent[child].dep = label
        # Keep a bit-vector tracking child dependencies.  If a word has a child at
        # offset i from it, set that bit (tracking left and right separately)
        if child > head:
            self._sent[head].r_kids |= 1 << (-dist)
        else:
            self._sent[head].l_kids |= 1 << dist

    cdef void del_arc(self, int head, int child) nogil:
        cdef int dist = head - child
        if child > head:
            self._sent[head].r_kids &= ~(1 << (-dist))
        else:
            self._sent[head].l_kids &= ~(1 << dist)

    cdef void open_ent(self, int label) nogil:
        self._ents[self._e_i].start = self.B(0)
        self._ents[self._e_i].label = label
        self._ents[self._e_i].end = 0
        self._e_i += 1

    cdef void close_ent(self) nogil:
        self._ents[self._e_i].end = self.B(0)+1
        self._sent[self.B(0)].ent_iob = 1

    cdef void set_ent_tag(self, int i, int ent_iob, int ent_type) nogil:
        if 0 <= i < self.length:
            self._sent[i].ent_iob = ent_iob
            self._sent[i].ent_type = ent_type

    cdef void set_break(self, int i) nogil:
        if 0 <= i < self.length:
            self._sent[i].sent_end = True
            self._break = i

    cdef void clone(self, StateClass src) nogil:
        memcpy(self._sent, src._sent, self.length * sizeof(TokenC))
        memcpy(self._stack, src._stack, self.length * sizeof(int))
        memcpy(self._buffer, src._buffer, self.length * sizeof(int))
        memcpy(self._ents, src._ents, self.length * sizeof(Entity))
        self._b_i = src._b_i
        self._s_i = src._s_i
        self._e_i = src._e_i

    def print_state(self, words):
        words = list(words) + ['_']
        top = words[self.S(0)] + '_%d' % self.S_(0).head
        second = words[self.S(1)] + '_%d' % self.S_(1).head
        third = words[self.S(2)] + '_%d' % self.S_(2).head
        n0 = words[self.B(0)] 
        n1 = words[self.B(1)] 
        return ' '.join((str(self.buffer_length()), str(self.stack_depth()), third, second, top, '|', n0, n1))
 

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
            if n < 1:
                return i
            n -= 1
    return 0


