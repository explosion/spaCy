from libcpp.vector cimport vector
from libc.stdint cimport uint32_t
from libc.stdint cimport uint64_t

from sparsehash.dense_hash_map cimport dense_hash_map

# Circular import problems here
ctypedef size_t Lexeme_addr
ctypedef uint32_t StringHash
ctypedef dense_hash_map[StringHash, size_t] Vocab
from spacy.lexeme cimport Lexeme

from spacy.tokens cimport Tokens

# Put these above import to avoid circular import problem
ctypedef char Bits8
ctypedef uint64_t Bits64
ctypedef int ClusterID


from spacy.lexeme cimport Lexeme
from spacy.lexeme cimport Distribution
from spacy.lexeme cimport Orthography


cdef class Language:
    cdef object name
    cdef dense_hash_map[StringHash, size_t] chunks
    cdef dense_hash_map[StringHash, size_t] vocab
    cdef dict bacov

    cdef Tokens tokenize(self, unicode text)

    cdef Lexeme* lookup(self, unicode string) except NULL
    cdef Lexeme** lookup_chunk(self, unicode chunk) except NULL
    
    cdef Lexeme** new_chunk(self, unicode string, list substrings) except NULL
    cdef Lexeme* new_lexeme(self, unicode lex) except NULL
    
    cdef unicode unhash(self, StringHash hashed)
    
    cpdef list find_substrings(self, unicode word)
    cdef int find_split(self, unicode word)
