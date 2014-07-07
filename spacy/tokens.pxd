from libcpp.vector cimport vector
from spacy.lexeme cimport Lexeme
from spacy.lexeme cimport Lexeme_addr

from cython.operator cimport dereference as deref
from spacy.spacy cimport Language

cdef enum Field:
    lex


cdef class Tokens:
    cdef Language lang
    cdef vector[Lexeme_addr]* vctr
    cdef size_t length
    
    cpdef int append(self, Lexeme_addr token)
    cpdef int extend(self, Tokens other) except -1
    
    cpdef list group_by(self, Field attr)
    cpdef dict count_by(self, Field attr)
