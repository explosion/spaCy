from libc.string cimport memcpy, memset
from libc.stdint cimport uint32_t
from ..vocab cimport EMPTY_LEXEME
from ..structs cimport Entity
from ..lexeme cimport Lexeme
from ..symbols cimport punct
from ..attrs cimport IS_SPACE


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

    def print_state(self, words):
        words = list(words) + ['_']
        top = words[self.S(0)] + '_%d' % self.S_(0).head
        second = words[self.S(1)] + '_%d' % self.S_(1).head
        third = words[self.S(2)] + '_%d' % self.S_(2).head
        n0 = words[self.B(0)] 
        n1 = words[self.B(1)] 
        return ' '.join((third, second, top, '|', n0, n1))
