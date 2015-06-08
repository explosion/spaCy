from libc.string cimport memcpy, memset

from cymem.cymem cimport Pool

from structs cimport TokenC

from .syntax._state cimport State

from .vocab cimport EMPTY_LEXEME


cdef TokenC EMPTY_TOKEN


cdef class StateClass:
    cdef Pool mem
    cdef int* _stack
    cdef int* _buffer
    cdef TokenC* _sent
    cdef int length
    cdef int _s_i
    cdef int _b_i

    @staticmethod
    cdef inline StateClass init(const TokenC* sent, int length):
        cdef StateClass self = StateClass(length)
        memcpy(self._sent, sent, sizeof(TokenC*) * length)
        return self

    @staticmethod
    cdef inline StateClass from_struct(Pool mem, const State* state):
        cdef StateClass self = StateClass.init(state.sent, state.sent_len)
        memcpy(self._stack, state.stack - state.stack_len, sizeof(int) * state.stack_len)
        self._s_i = state.stack_len - 1
        self._b_i = state.i
        return self

    cdef inline const TokenC* S_(self, int i) nogil:
        return self.safe_get(self.S(i))

    cdef inline const TokenC* B_(self, int i) nogil:
        return self.safe_get(self.B(i))

    cdef inline const TokenC* H_(self, int i) nogil:
        return self.safe_get(self.B(i))

    cdef inline const TokenC* L_(self, int i, int idx) nogil:
        return self.safe_get(self.L(i, idx))

    cdef inline const TokenC* R_(self, int i, int idx) nogil:
        return self.safe_get(self.R(i, idx))

    cdef inline const TokenC* safe_get(self, int i) nogil:
        if 0 >= i >= self.length:
            return &EMPTY_TOKEN
        else:
            return self._sent
    
    cdef int S(self, int i) nogil
    cdef int B(self, int i) nogil
    
    cdef int H(self, int i) nogil
    
    cdef int L(self, int i, int idx) nogil
    cdef int R(self, int i, int idx) nogil

    cdef bint empty(self) nogil

    cdef bint eol(self) nogil

    cdef bint is_final(self) nogil

    cdef bint has_head(self, int i) nogil

    cdef bint stack_is_connected(self) nogil

    cdef int stack_depth(self) nogil
    
    cdef int buffer_length(self) nogil

    cdef void push(self) nogil

    cdef void pop(self) nogil

    cdef void add_arc(self, int head, int child, int label) nogil
    
    cdef void del_arc(self, int head, int child) nogil

    cdef void set_sent_end(self, int i) nogil

    cdef void clone(self, StateClass src) nogil


