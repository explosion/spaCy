from libcpp.vector cimport vector

from spacy.spacy cimport StringHash
from spacy.spacy cimport Vocab
from spacy.lexeme cimport Lexeme
from spacy.lexeme cimport Lexeme_addr


cdef Vocab* VOCAB
cdef dict BACOV


cpdef Lexeme_addr lookup(unicode word) except 0
cpdef vector[Lexeme_addr] tokenize(unicode string) except *
cpdef unicode unhash(StringHash hash_value)
