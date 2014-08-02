from libcpp.vector cimport vector
from libc.stdint cimport uint64_t

from sparsehash.dense_hash_map cimport dense_hash_map

# Circular import problems here
ctypedef size_t Lexeme_addr
ctypedef uint64_t StringHash
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
    cdef Vocab* vocab
    cdef Vocab* distri
    cdef Vocab* ortho
    cdef dict bacov
    cdef int find_split(self, unicode word, size_t length)

    cdef Lexeme_addr lookup(self, int split, Py_UNICODE* string, size_t length) except 0
    cdef StringHash hash_string(self, Py_UNICODE* string, size_t length) except 0
    cdef unicode unhash(self, StringHash hashed)
    
    cpdef Tokens tokenize(self, unicode text)
    cdef Lexeme* _add(self, StringHash hashed, unicode string, int split, size_t length)
    cdef Lexeme* init_lexeme(self, unicode string, StringHash hashed,
                             int split, size_t length)
    cdef Orthography* init_orth(self, StringHash hashed, unicode lex)
