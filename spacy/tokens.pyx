from cython.operator cimport dereference as deref
from cython.operator cimport preincrement as inc


from spacy.lexeme cimport Lexeme
from spacy.lexeme cimport attr_of, norm_of, shape_of
from spacy.spacy cimport StringHash


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

    cpdef list group_by(self, StringAttr attr):
        cdef dict indices = {}
        cdef vector[vector[Lexeme_addr]] groups = vector[vector[Lexeme_addr]]()

        cdef StringHash key
        cdef Lexeme_addr t
        for t in self.vctr[0]:
            key = attr_of(t, attr)
            if key in indices:
                groups[indices[key]].push_back(t)
            else:
                indices[key] = groups.size()
                groups.push_back(vector[Lexeme_addr]())
                groups.back().push_back(t)
        return groups

    cpdef dict count_by(self, StringAttr attr):
        counts = {}
        cdef Lexeme_addr t
        cdef StringHash key
        for t in self.vctr[0]:
            key = attr_of(t, attr)
            if key not in counts:
                counts[key] = 0
            counts[key] += 1
        return counts
