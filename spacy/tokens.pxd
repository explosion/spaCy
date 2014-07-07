from libcpp.vector cimport vector
from spacy.spacy cimport Lexeme_addr

from cython.operator cimport dereference as deref
from spacy.spacy cimport Language
from spacy.lexeme cimport StringAttr


cdef class Tokens:
    cdef Language lang
    cdef vector[Lexeme_addr]* vctr
    cdef size_t length
    
    cpdef int append(self, Lexeme_addr token)
    cpdef int extend(self, Tokens other) except -1
    
    cpdef list group_by(self, StringAttr attr)
    cpdef dict count_by(self, StringAttr attr)
