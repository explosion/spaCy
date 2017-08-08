# coding: utf-8
# cython: infer_types=True
from __future__ import unicode_literals

from libc.string cimport memcpy, memset
from libc.stdint cimport uint32_t, uint64_t

from ..vocab cimport EMPTY_LEXEME
from ..structs cimport Entity
from ..lexeme cimport Lexeme
from ..symbols cimport punct
from ..attrs cimport IS_SPACE
from ..attrs cimport attr_id_t
from ..tokens.token cimport Token
from ..tokens.doc cimport Doc


cdef class StateClass:
    def __init__(self, Doc doc=None, int offset=0):
        cdef Pool mem = Pool()
        self.mem = mem
        if doc is not None:
            self.c = new StateC(doc.c, doc.length)
            self.c.offset = offset

    def __dealloc__(self):
        del self.c

    @property
    def stack(self):
        return {self.S(i) for i in range(self.c._s_i)}

    @property
    def queue(self):
        return {self.B(i) for i in range(self.c.buffer_length())}

    @property
    def token_vector_lenth(self):
        return self.doc.tensor.shape[1]

    def is_final(self):
        return self.c.is_final()

    def copy(self):
        cdef StateClass new_state = StateClass.init(self.c._sent, self.c.length)
        new_state.c.clone(self.c)
        return new_state

    def print_state(self, words):
        words = list(words) + ['_']
        top = words[self.S(0)] + '_%d' % self.S_(0).head
        second = words[self.S(1)] + '_%d' % self.S_(1).head
        third = words[self.S(2)] + '_%d' % self.S_(2).head
        n0 = words[self.B(0)]
        n1 = words[self.B(1)]
        return ' '.join((third, second, top, '|', n0, n1))

    @classmethod
    def nr_context_tokens(cls):
        return 13

    def set_context_tokens(self, int[::1] output):
        output[0] = self.B(0)
        output[1] = self.B(1)
        output[2] = self.S(0)
        output[3] = self.S(1)
        output[4] = self.S(2)
        output[5] = self.L(self.S(0), 1)
        output[6] = self.L(self.S(0), 2)
        output[6] = self.R(self.S(0), 1)
        output[7] = self.L(self.B(0), 1)
        output[8] = self.R(self.S(0), 2)
        output[9] = self.L(self.S(1), 1)
        output[10] = self.L(self.S(1), 2)
        output[11] = self.R(self.S(1), 1)
        output[12] = self.R(self.S(1), 2)

        for i in range(13):
            if output[i] != -1:
                output[i] += self.c.offset
