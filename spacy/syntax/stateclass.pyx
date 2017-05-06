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


cdef class StateClass:
    def __init__(self, int length):
        cdef Pool mem = Pool()
        self.mem = mem

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

    def py_is_final(self):
        return self.c.is_final()

    def print_state(self, words):
        words = list(words) + ['_']
        top = words[self.S(0)] + '_%d' % self.S_(0).head
        second = words[self.S(1)] + '_%d' % self.S_(1).head
        third = words[self.S(2)] + '_%d' % self.S_(2).head
        n0 = words[self.B(0)]
        n1 = words[self.B(1)]
        return ' '.join((third, second, top, '|', n0, n1))

    def nr_context_tokens(self, int nF, int nB, int nS, int nL, int nR):
        return 8

    def set_context_tokens(self, int[:] output, nF=1, nB=0, nS=2,
            nL=2, nR=2):
        output[0] = self.B(0)
        output[1] = self.B(1)
        output[2] = self.S(0)
        output[3] = self.S(1)
        output[4] = self.L(self.S(0), 1)
        output[5] = self.L(self.S(0), 2)
        output[6] = self.R(self.S(0), 1)
        output[7] = self.R(self.S(0), 2)
        #output[7] = self.L(self.S(1), 1)
        #output[8] = self.L(self.S(1), 2)
        #output[9] = self.R(self.S(1), 1)
        #output[10] = self.R(self.S(1), 2)

    def set_attributes(self, uint64_t[:, :] vals, int[:] tokens, int[:] names):
        cdef int i, j, tok_i
        for i in range(tokens.shape[0]):
            tok_i = tokens[i]
            if tok_i >= 0:
                token = &self.c._sent[tok_i]
                for j in range(names.shape[0]):
                    vals[i, j] = Token.get_struct_attr(token, <attr_id_t>names[j])
            else:
                vals[i] = 0

    def set_token_vectors(self, float[:, :] tokvecs,
            float[:, :] all_tokvecs, int[:] indices):
        for i in range(indices.shape[0]):
            if indices[i] >= 0:
                tokvecs[i] = all_tokvecs[indices[i]]
            else:
                tokvecs[i] = 0
