from ext.sparsehash cimport dense_hash_map
from spacy.lexeme cimport StringHash
from spacy.lexeme cimport Lexeme


ctypedef Py_UNICODE* string_ptr
ctypedef size_t Lexeme_addr # For python interop 
ctypedef Lexeme* Lexeme_ptr


cdef dense_hash_map[StringHash, Lexeme_ptr] LEXEMES


cpdef Lexeme_addr lookup(unicode word) except 0
cpdef Lexeme_addr lookup_chunk(unicode chunk, int start, int end) except 0
cdef StringHash hash_string(unicode s, size_t length) except 0
cpdef unicode unhash(StringHash hash_value)
