from libcpp.vector cimport vector
from libc.stdint cimport uint64_t

from ext.sparsehash cimport dense_hash_map


# Circular import problems here
ctypedef size_t Lexeme_addr
ctypedef uint64_t StringHash
ctypedef dense_hash_map[StringHash, Lexeme_addr] Vocab
ctypedef int (*Splitter)(unicode word, size_t length)


from spacy.lexeme cimport Lexeme
from spacy.tokens cimport Tokens

cdef class Language:
    cdef object name
    cdef Vocab* vocab
    cdef dict bacov
    cdef int find_split(self, unicode word, size_t length)

    cdef Lexeme_addr lookup(self, int split, Py_UNICODE* string, size_t length) except 0
    cdef StringHash hash_string(self, Py_UNICODE* string, size_t length) except 0
    cdef unicode unhash(self, StringHash hashed)
    
    cpdef Tokens tokenize(self, unicode text)
    cdef Lexeme* _add(self, StringHash hashed, unicode string, int split, size_t length)
