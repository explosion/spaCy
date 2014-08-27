from spacy.lang cimport Language
from spacy.word cimport Lexeme
cimport cython


cdef class English(Language):
    cpdef int _split_one(self, unicode word)
