from libc.stdint cimport uint32_t
from libc.stdint cimport uint64_t
from spacy.word cimport Lexeme
from spacy.tokens cimport Tokens
from spacy.lexeme cimport LexemeC
from spacy._hashing cimport PointerHash

from libcpp.utility cimport pair
from libcpp.vector cimport vector
from libc.stdint cimport uint64_t, int64_t


cdef extern from "Python.h":
    cdef bint Py_UNICODE_ISSPACE(Py_UNICODE ch)
    cdef bint Py_UNICODE_ISALNUM(Py_UNICODE ch)


cdef struct String:
    Py_UNICODE* chars
    size_t n
    uint64_t key


cdef class Lexicon:
    cpdef readonly size_t size

    cpdef Lexeme lookup(self, unicode string)
    cdef LexemeC* get(self, String* s)
    
    cdef PointerHash _dict
    
    cdef list _string_features
    cdef list _flag_features


cdef class Language:
    cdef unicode name
    cdef PointerHash cache
    cdef PointerHash specials
    cpdef readonly Lexicon lexicon

    cpdef Tokens tokenize(self, unicode text)
    cpdef Lexeme lookup(self, unicode text)

    cdef int _tokenize(self, Tokens tokens, String* string)
    cdef int _split_one(self, Py_UNICODE* characters, size_t length)
