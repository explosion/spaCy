from spacy.lang cimport Language
from spacy.word cimport Lexeme
cimport cython


cdef class English(Language):
    cdef int _split_one(self, unicode word)
