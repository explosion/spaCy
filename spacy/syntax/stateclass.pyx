# coding: utf-8
# cython: infer_types=True
from __future__ import unicode_literals

import numpy

from ..tokens.doc cimport Doc


cdef class StateClass:
    def __init__(self, Doc doc=None, int offset=0, int max_split=0):
        cdef Pool mem = Pool()
        self.mem = mem
        self._borrowed = 0
        if doc is not None:
            self.c = new StateC(doc.c, doc.length)
            self.c.offset = offset
            self.c.max_split = max_split

    def __dealloc__(self):
        if self._borrowed != 1:
            del self.c

    def __len__(self):
        return self.c.length

    def get_B(self, int i):
        return self.c.B(i)
    
    def get_S(self, int i):
        return self.c.S(i)

    def can_push(self):
        return self.c.can_push()

    def can_pop(self):
        return self.c.can_pop()

    def can_break(self):
        return self.c.can_break()

    def can_arc(self):
        return self.c.can_arc()

    def push_stack(self):
        self.c.push()

    def pop_stack(self):
        self.c.pop()

    def unshift(self):
        self.c.unshift()

    def set_break(self, int i):
        self.c.set_break(i)

    def split_token(self, int i, int n):
        self.c.split(i, n)

    def get_doc(self, vocab):
        cdef Doc doc = Doc(vocab)
        doc.vocab = vocab
        doc.c = self.c._sent
        doc.length = self.c.length
        return doc

    @property
    def buffer_length(self):
        return self.c.buffer_length

    @property
    def stack(self):
        return [self.S(i) for i in range(self.c._s_i)]

    @property
    def queue(self):
        return [self.B(i) for i in range(self.c.buffer_length)]

    @property
    def token_vector_lenth(self):
        return self.doc.tensor.shape[1]

    @property
    def history(self):
        hist = numpy.ndarray((8,), dtype='i')
        for i in range(8):
            hist[i] = self.c.get_hist(i+1)
        return hist

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
