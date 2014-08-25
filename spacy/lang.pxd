from libc.stdint cimport uint32_t
from libc.stdint cimport uint64_t
from spacy.word cimport Lexeme


cdef class Language:
    cdef object name
    cdef dict blobs
    cdef dict lexicon

    cpdef list tokenize(self, unicode text)

    cdef Word lookup(self, unicode string)
    cdef list lookup_chunk(self, unicode chunk)
    
    cdef list new_chunk(self, unicode string, list substrings)
    cdef Word new_lexeme(self, unicode lex)
    
    cpdef list find_substrings(self, unicode chunk)
    cdef int find_split(self, unicode word)
