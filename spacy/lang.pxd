from libc.stdint cimport uint32_t
from libc.stdint cimport uint64_t
from spacy.word cimport Lexeme
from spacy.tokens cimport Tokens


cdef struct Flags:
    size_t is_alpha
    size_t can_noun


cdef struct ViewIDs:
    size_t canon_form


cdef class Lexicon:
    cpdef readonly size_t size

    cpdef Lexeme lookup(self, unicode string)
    
    cdef dict _dict
    
    cdef list _string_features
    cdef list _flag_features


cdef class Language:
    cdef unicode name
    cdef dict cache
    cpdef readonly Lexicon lexicon
    cpdef readonly object tokens_class

    cpdef list tokenize(self, unicode text)
    cpdef Lexeme lookup(self, unicode text)

    cdef _tokenize(self, Tokens tokens, unicode string)
    cdef list _split(self, unicode string)
    cdef int _split_one(self, unicode word)
