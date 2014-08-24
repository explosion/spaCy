from libcpp.vector cimport vector

from spacy.spacy cimport StringHash

from spacy.spacy cimport Language
from spacy.word cimport LatinWord
cimport cython


cdef class English(spacy.Language):
    cdef int find_split(self, unicode word)
    cdef LatinWord new_lexeme(self, unicode string)


cdef English EN


cpdef Word lookup(unicode word)
cpdef list tokenize(unicode string)
cpdef unicode unhash(StringHash hash_value)
