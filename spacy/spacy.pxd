from libc.stdint cimport uint32_t
from libc.stdint cimport uint64_t
from spacy.word cimport Word

ctypedef uint32_t StringHash



cdef class Language:
    cdef object name
    cdef dict chunks
    cdef dict vocab
    cdef dict bacov

    cpdef list tokenize(self, unicode text)

    cdef Word lookup(self, unicode string)
    cdef list lookup_chunk(self, unicode chunk)
    
    cdef list new_chunk(self, unicode string, list substrings)
    cdef Word new_lexeme(self, unicode lex)
    
    cpdef unicode unhash(self, StringHash hashed)
    
    cpdef list find_substrings(self, unicode chunk)
    cdef int find_split(self, unicode word)
    cdef int set_orth(self, unicode string, Word word)
