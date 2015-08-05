from libc.string cimport memcpy, memset

from cymem.cymem cimport Pool

from ..structs cimport TokenC, Entity

from ..vocab cimport EMPTY_LEXEME


cdef class StateClass:
    cdef Pool mem
    cdef int* _stack
    cdef int* _buffer
    cdef bint* shifted
    cdef TokenC* _sent
    cdef Entity* _ents
    cdef TokenC _empty_token
    cdef int length
    cdef int _s_i
    cdef int _b_i
    cdef int _e_i
    cdef int _break

    @staticmethod
    cdef inline StateClass init(const TokenC* sent, int length):
        cdef StateClass self = StateClass(length)
        cdef int i
        for i in range(length):
            self._sent[i] = sent[i]
            self._buffer[i] = i
        for i in range(length, length + 5):
            self._sent[i].lex = &EMPTY_LEXEME
        return self

    cdef inline int S(self, int i) nogil:
        if i >= self._s_i:
            return -1
        return self._stack[self._s_i - (i+1)]

    cdef inline int B(self, int i) nogil:
        if (i + self._b_i) >= self.length:
            return -1
        return self._buffer[self._b_i + i]

    cdef inline const TokenC* S_(self, int i) nogil:
        return self.safe_get(self.S(i))

    cdef inline const TokenC* B_(self, int i) nogil:
        return self.safe_get(self.B(i))

    cdef inline const TokenC* H_(self, int i) nogil:
        return self.safe_get(self.H(i))

    cdef inline const TokenC* E_(self, int i) nogil:
        return self.safe_get(self.E(i))

    cdef inline const TokenC* L_(self, int i, int idx) nogil:
        return self.safe_get(self.L(i, idx))

    cdef inline const TokenC* R_(self, int i, int idx) nogil:
        return self.safe_get(self.R(i, idx))

    cdef inline const TokenC* safe_get(self, int i) nogil:
        if i < 0 or i >= self.length:
            return &self._empty_token
        else:
            return &self._sent[i]

    cdef inline int H(self, int i) nogil:
        if i < 0 or i >= self.length:
            return -1
        return self._sent[i].head + i


    cdef int E(self, int i) nogil

    cdef int R(self, int i, int idx) nogil
    
    cdef int L(self, int i, int idx) nogil

    cdef inline bint empty(self) nogil:
        return self._s_i <= 0

    cdef inline bint eol(self) nogil:
        return self.buffer_length() == 0

    cdef inline bint at_break(self) nogil:
        return self._break != -1

    cdef inline bint is_final(self) nogil:
        return self.stack_depth() <= 0 and self._b_i >= self.length

    cdef inline bint has_head(self, int i) nogil:
        return self.safe_get(i).head != 0

    cdef inline int n_L(self, int i) nogil:
        return self.safe_get(i).l_kids

    cdef inline int n_R(self, int i) nogil:
        return self.safe_get(i).r_kids

    cdef inline bint stack_is_connected(self) nogil:
        return False

    cdef inline bint entity_is_open(self) nogil:
        if self._e_i < 1:
            return False
        return self._ents[self._e_i-1].end == -1

    cdef inline int stack_depth(self) nogil:
        return self._s_i

    cdef inline int buffer_length(self) nogil:
        if self._break != -1:
            return self._break - self._b_i
        else:
            return self.length - self._b_i

    cdef void push(self) nogil

    cdef void pop(self) nogil
    
    cdef void unshift(self) nogil

    cdef void add_arc(self, int head, int child, int label) nogil
    
    cdef void del_arc(self, int head, int child) nogil

    cdef void open_ent(self, int label) nogil
    
    cdef void close_ent(self) nogil
    
    cdef void set_ent_tag(self, int i, int ent_iob, int ent_type) nogil

    cdef void set_break(self, int i) nogil

    cdef void clone(self, StateClass src) nogil

    cdef void fast_forward(self) nogil
