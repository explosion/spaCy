from libc.stdint cimport uint32_t
from libc.stdint cimport uint64_t
from spacy.word cimport Lexeme


cdef class Lexicon:
    cpdef Lexeme lookup(self, unicode string)
    
    cdef dict _dict
    
    cdef list _string_features
    cdef list _flag_features


cdef class Language:
    cdef unicode name
    cdef dict cache
    cpdef readonly Lexicon lexicon

    cpdef list tokenize(self, unicode text)
    cpdef Lexeme lookup(self, unicode text)

    cdef list _tokenize(self, unicode string)
    cdef list _split(self, unicode string)
    cdef int _split_one(self, unicode word)
