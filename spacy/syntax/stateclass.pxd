from libc.string cimport memcpy, memset

from cymem.cymem cimport Pool
cimport cython

from ..structs cimport TokenC, SpanC
from ..typedefs cimport attr_t

from ..vocab cimport EMPTY_LEXEME
from ._state cimport StateC


cdef class StateClass:
    cdef Pool mem
    cdef StateC* c
    cdef int _borrowed

    @staticmethod
    cdef inline StateClass init(const TokenC* sent, int length):
        cdef StateClass self = StateClass()
        self.c = new StateC(sent, length)
        return self
    
    @staticmethod
    cdef inline StateClass borrow(StateC* ptr):
        cdef StateClass self = StateClass()
        del self.c
        self.c = ptr
        self._borrowed = 1
        return self


    @staticmethod
    cdef inline StateClass init_offset(const TokenC* sent, int length, int
                                       offset):
        cdef StateClass self = StateClass()
        self.c = new StateC(sent, length)
        self.c.offset = offset
        return self

    cdef inline int S(self, int i) nogil:
        return self.c.S(i)

    cdef inline int B(self, int i) nogil:
        return self.c.B(i)

    cdef inline const TokenC* S_(self, int i) nogil:
        return self.c.S_(i)

    cdef inline const TokenC* B_(self, int i) nogil:
        return self.c.B_(i)

    cdef inline const TokenC* H_(self, int i) nogil:
        return self.c.H_(i)

    cdef inline const TokenC* E_(self, int i) nogil:
        return self.c.E_(i)

    cdef inline const TokenC* L_(self, int i, int idx) nogil:
        return self.c.L_(i, idx)

    cdef inline const TokenC* R_(self, int i, int idx) nogil:
        return self.c.R_(i, idx)

    cdef inline const TokenC* safe_get(self, int i) nogil:
        return self.c.safe_get(i)

    cdef inline int H(self, int i) nogil:
        return self.c.H(i)
    
    cdef inline int E(self, int i) nogil:
        return self.c.E(i)

    cdef inline int L(self, int i, int idx) nogil:
        return self.c.L(i, idx)

    cdef inline int R(self, int i, int idx) nogil:
        return self.c.R(i, idx)

    cdef inline bint empty(self) nogil:
        return self.c.empty()

    cdef inline bint eol(self) nogil:
        return self.c.eol()

    cdef inline bint at_break(self) nogil:
        return self.c.at_break()

    cdef inline bint has_head(self, int i) nogil:
        return self.c.has_head(i)

    cdef inline int n_L(self, int i) nogil:
        return self.c.n_L(i)

    cdef inline int n_R(self, int i) nogil:
        return self.c.n_R(i)

    cdef inline bint stack_is_connected(self) nogil:
        return False

    cdef inline bint entity_is_open(self) nogil:
        return self.c.entity_is_open()

    cdef inline int stack_depth(self) nogil:
        return self.c.stack_depth()

    cdef inline int buffer_length(self) nogil:
        return self.c.buffer_length()

    cdef inline void push(self) nogil:
        self.c.push()

    cdef inline void pop(self) nogil:
        self.c.pop()

    cdef inline void unshift(self) nogil:
        self.c.unshift()

    cdef inline void add_arc(self, int head, int child, attr_t label) nogil:
        self.c.add_arc(head, child, label)

    cdef inline void del_arc(self, int head, int child) nogil:
        self.c.del_arc(head, child)

    cdef inline void open_ent(self, attr_t label) nogil:
        self.c.open_ent(label)

    cdef inline void close_ent(self) nogil:
        self.c.close_ent()

    cdef inline void set_ent_tag(self, int i, int ent_iob, attr_t ent_type) nogil:
        self.c.set_ent_tag(i, ent_iob, ent_type)

    cdef inline void set_break(self, int i) nogil:
        self.c.set_break(i)

    cdef inline void clone(self, StateClass src) nogil:
        self.c.clone(src.c)

    cdef inline void fast_forward(self) nogil:
        self.c.fast_forward()
