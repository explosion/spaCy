from libc.string cimport memcpy, memset
from libc.stdint cimport uint32_t
from ..vocab cimport EMPTY_LEXEME
from ..structs cimport Entity


cdef class StateClass:
    def __init__(self, int length):
        cdef Pool mem = Pool()
        cdef int PADDING = 5
        self._buffer = <int*>mem.alloc(length + (PADDING * 2), sizeof(int))
        self._stack = <int*>mem.alloc(length + (PADDING * 2), sizeof(int))
        self.shifted = <bint*>mem.alloc(length + (PADDING * 2), sizeof(bint))
        self._sent = <TokenC*>mem.alloc(length + (PADDING * 2), sizeof(TokenC))
        self._ents = <Entity*>mem.alloc(length + (PADDING * 2), sizeof(Entity))
        cdef int i
        for i in range(length + (PADDING * 2)):
            self._ents[i].end = -1
        for i in range(length, length + (PADDING * 2)):
            self._sent[i].lex = &EMPTY_LEXEME
        self._sent += PADDING
        for i in range(length):
            self._sent[i].l_edge = i
            self._sent[i].r_edge = i
        self._ents += PADDING
        self._buffer += PADDING
        self._stack += PADDING
        self.shifted += PADDING
        self.mem = mem
        self.length = length
        self._break = -1
        self._s_i = 0
        self._b_i = 0
        self._e_i = 0
        for i in range(length):
            self._buffer[i] = i
        self._empty_token.lex = &EMPTY_LEXEME

    @property
    def stack(self):
        return {self.S(i) for i in range(self._s_i)}

    @property
    def queue(self):
        return {self.B(i) for i in range(self._b_i, self.length)}

    cdef int E(self, int i) nogil:
        if self._e_i <= 0 or self._e_i >= self.length:
            return 0
        if i < 0 or i >= self.length:
            return 0
        return self._ents[self._e_i-1].start

    cdef int L(self, int i, int idx) nogil:
        if idx < 1:
            return -1
        if i < 0 or i >= self.length:
            return -1
        cdef const TokenC* target = &self._sent[i]
        if target.l_kids < idx:
            return -1
        cdef const TokenC* ptr = &self._sent[target.l_edge]

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
        cdef const TokenC* target = &self._sent[i]
        if target.r_kids < idx:
            return -1
        cdef const TokenC* ptr = &self._sent[target.r_edge]
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

    cdef void push(self) nogil:
        if self.B(0) != -1:
            self._stack[self._s_i] = self.B(0)
        self._s_i += 1
        self._b_i += 1
        if self._b_i > self._break:
            self._break = -1

    cdef void pop(self) nogil:
        if self._s_i >= 1:
            self._s_i -= 1

    cdef void unshift(self) nogil:
        self._b_i -= 1
        self._buffer[self._b_i] = self.S(0)
        self._s_i -= 1
        self.shifted[self.B(0)] = True

    cdef void fast_forward(self) nogil:
        while self.buffer_length() == 0 or self.stack_depth() == 0:
            if self.buffer_length() == 1 and self.stack_depth() == 0:
                self.push()
                self.pop()
            elif self.buffer_length() == 0 and self.stack_depth() == 1:
                self.pop()
            elif self.buffer_length() == 0 and self.stack_depth() >= 2:
                if self.has_head(self.S(0)):
                    self.pop()
                else:
                    self.unshift()
            elif (self.length - self._b_i) >= 1 and self.stack_depth() == 0:
                self.push()
            else:
                break

    cdef void add_arc(self, int head, int child, int label) nogil:
        if self.has_head(child):
            self.del_arc(self.H(child), child)

        cdef int dist = head - child
        self._sent[child].head = dist
        self._sent[child].dep = label
        cdef int i
        if child > head:
            self._sent[head].r_kids += 1
            # Some transition systems can have a word in the buffer have a
            # rightward child, e.g. from Unshift.
            self._sent[head].r_edge = self._sent[child].r_edge
            i = 0
            while self.has_head(head) and i < self.length:
                head = self.H(head)
                self._sent[head].r_edge = self._sent[child].r_edge
                i += 1 # Guard against infinite loops
        else:
            self._sent[head].l_kids += 1
            self._sent[head].l_edge = self._sent[child].l_edge

    cdef void del_arc(self, int h_i, int c_i) nogil:
        cdef int dist = h_i - c_i
        cdef TokenC* h = &self._sent[h_i]
        if c_i > h_i:
            h.r_kids -= 1
            h.r_edge = self.R_(h_i, 2).r_edge if h.r_kids >= 1 else h_i
        else:
            h.l_kids -= 1
            h.l_edge = self.L_(h_i, 2).l_edge if h.l_kids >= 1 else h_i

    cdef void open_ent(self, int label) nogil:
        self._ents[self._e_i].start = self.B(0)
        self._ents[self._e_i].label = label
        self._ents[self._e_i].end = -1
        self._e_i += 1

    cdef void close_ent(self) nogil:
        self._ents[self._e_i-1].end = self.B(0)+1
        self._sent[self.B(0)].ent_iob = 1

    cdef void set_ent_tag(self, int i, int ent_iob, int ent_type) nogil:
        if 0 <= i < self.length:
            self._sent[i].ent_iob = ent_iob
            self._sent[i].ent_type = ent_type

    cdef void set_break(self, int _) nogil:
        if 0 <= self.B(0) < self.length: 
            self._sent[self.B(0)].sent_start = True
            self._break = self._b_i

    cdef void clone(self, StateClass src) nogil:
        memcpy(self._sent, src._sent, self.length * sizeof(TokenC))
        memcpy(self._stack, src._stack, self.length * sizeof(int))
        memcpy(self._buffer, src._buffer, self.length * sizeof(int))
        memcpy(self._ents, src._ents, self.length * sizeof(Entity))
        self._b_i = src._b_i
        self._s_i = src._s_i
        self._e_i = src._e_i
        self._break = src._break

    def print_state(self, words):
        words = list(words) + ['_']
        top = words[self.S(0)] + '_%d' % self.S_(0).head
        second = words[self.S(1)] + '_%d' % self.S_(1).head
        third = words[self.S(2)] + '_%d' % self.S_(2).head
        n0 = words[self.B(0)] 
        n1 = words[self.B(1)] 
        return ' '.join((third, second, top, '|', n0, n1))
