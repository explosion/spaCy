from libcpp.vector cimport vector
from libc.stdint cimport uint32_t
from libc.stdint cimport uint64_t

# Circular import problems here
ctypedef size_t Lexeme_addr
ctypedef uint32_t StringHash
from spacy.lexeme cimport Lexeme

from spacy.tokens cimport Tokens

# Put these above import to avoid circular import problem
ctypedef char Bits8
ctypedef uint64_t Bits64
ctypedef int ClusterID


from spacy.lexeme cimport Lexeme


cdef class Language:
    cdef object name
    cdef dict chunks
    cdef dict vocab
    cdef dict bacov

    cpdef Tokens tokenize(self, unicode text)

    cdef Lexeme* lookup(self, unicode string) except NULL
    cdef Lexeme** lookup_chunk(self, unicode chunk) except NULL
    
    cdef Lexeme** new_chunk(self, unicode string, list substrings) except NULL
    cdef Lexeme* new_lexeme(self, unicode lex) except NULL
    
    cpdef unicode unhash(self, StringHash hashed)
    
    cpdef list find_substrings(self, unicode chunk)
    cdef int find_split(self, unicode word)
    cdef int set_orth(self, unicode string, Lexeme* word)
