from libc.string cimport memcpy, memset
from libc.stdint cimport uint32_t
from .vocab cimport EMPTY_LEXEME


memset(&EMPTY_TOKEN, 0, sizeof(TokenC))
EMPTY_TOKEN.lex = &EMPTY_LEXEME


cdef class StateClass:
    def __cinit__(self, int length):
        self.mem = Pool()
        self._stack = <int*>self.mem.alloc(sizeof(int), length)
        self._buffer = <int*>self.mem.alloc(sizeof(int), length)
        self._sent = <TokenC*>self.mem.alloc(sizeof(TokenC*), length)
        self.length = 0
        for i in range(self.length):
            self._buffer[i] = i

    cdef int S(self, int i) nogil:
        if self._s_i - (i+1) < 0:
            return -1
        return self._stack[self._s_i - (i+1)]

    cdef int B(self, int i) nogil:
        if (i + self._b_i) >= self.length:
            return -1
        return self._buffer[self._b_i + i]

    cdef int H(self, int i) nogil:
        if i < 0 or i >= self.length:
            return -1
        return self._sent[i].head + i

    cdef int L(self, int i, int idx) nogil:
        if 0 <= _popcount(self.safe_get(i).l_kids) <= idx:
            return -1
        return _nth_significant_bit(self.safe_get(i).l_kids, idx)

    cdef int R(self, int i, int idx) nogil:
        if 0 <= _popcount(self.safe_get(i).r_kids) <= idx:
            return -1
        return _nth_significant_bit(self.safe_get(i).r_kids, idx)

    cdef bint empty(self) nogil:
        return self._s_i <= 0

    cdef bint eol(self) nogil:
        return self._b_i >= self.length

    cdef bint is_final(self) nogil:
        return self.eol() and self.empty()

    cdef bint has_head(self, int i) nogil:
        return self.safe_get(i).head != 0

    cdef bint stack_is_connected(self) nogil:
        return False

    cdef int stack_depth(self) nogil:
        return self._s_i

    cdef int buffer_length(self) nogil:
        return self.length - self._b_i

    cdef void push(self) nogil:
        self._stack[self._s_i] = self.B(0)
        self._s_i += 1
        self._b_i += 1

    cdef void pop(self) nogil:
        self._s_i -= 1

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

    cdef void set_sent_end(self, int i) nogil:
        if 0 < i < self.length:
            self._sent[i].sent_end = True

    cdef void clone(self, StateClass src) nogil:
        memcpy(self._sent, src._sent, self.length * sizeof(TokenC))
        memcpy(self._stack, src._stack, self.length * sizeof(int))
        memcpy(self._buffer, src._buffer, self.length * sizeof(int))
        self._b_i = src._b_i
        self._s_i = src._s_i
 

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


