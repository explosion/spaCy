from cython.operator cimport dereference as deref
from cython.operator cimport preincrement as inc


cdef class Tokens:
    def __cinit__(self, Language lang):
        self.lang = lang
        self.vctr = new vector[Lexeme_addr]()
        self.length = 0

    def __dealloc__(self):
        del self.vctr

    def __iter__(self):
        cdef vector[Lexeme_addr].iterator it = self.vctr[0].begin()
        while it != self.vctr[0].end():
            yield deref(it)
            inc(it)

    def __getitem__(self, size_t idx):
        return self.vctr[0].at(idx)

    def __len__(self):
        return self.length

    cpdef int append(self, Lexeme_addr token):
        self.vctr[0].push_back(token)
        self.length += 1

    cpdef int extend(self, Tokens other) except -1:
        cdef Lexeme_addr el
        for el in other:
            self.append(el)

    cpdef list group_by(self, Field attr):
        pass

    cpdef dict count_by(self, Field attr):
        counts = {}
        cdef Lexeme_addr t
        cdef Lexeme* word
        for t in self.vctr[0]:
            word = <Lexeme*>t
            if word.lex not in counts:
                counts[word.lex] = 0
            counts[word.lex] += 1
        return counts

