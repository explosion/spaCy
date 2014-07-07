from libcpp.vector cimport vector
from libc.stdint cimport uint64_t

from ext.sparsehash cimport dense_hash_map

# Circular import problems here
ctypedef size_t Lexeme_addr
ctypedef uint64_t StringHash
ctypedef dense_hash_map[StringHash, Lexeme_addr] Vocab
ctypedef int (*Splitter)(unicode word, size_t length)


from spacy.lexeme cimport Lexeme

cdef load_tokenization(Vocab* vocab, dict bacov, token_rules)
cdef load_browns(Vocab* vocab, dict bacov, Splitter find_split)
cdef vector[Lexeme_addr] tokenize(Vocab* vocab, dict bacov, Splitter splitter,
                                  unicode string) except *
cdef Lexeme_addr lookup(Vocab* vocab, dict bacov, Splitter splitter, int start,
                        Py_UNICODE* string, size_t length) except 0
cdef StringHash hash_string(Py_UNICODE* s, size_t length) nogil
cdef unicode unhash(dict bacov, StringHash hash_value)
 
 
cpdef vector[size_t] expand_chunk(size_t addr) except *
