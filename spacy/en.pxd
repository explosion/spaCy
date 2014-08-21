from libcpp.vector cimport vector

from spacy.spacy cimport StringHash
from spacy.lexeme cimport Lexeme
from spacy.lexeme cimport LexID
from spacy.lexeme cimport ClusterID

from spacy.spacy cimport Language
from spacy.tokens cimport Tokens
cimport cython


cdef class English(spacy.Language):
    cdef int find_split(self, unicode word)
    cdef int set_orth(self, unicode word, Lexeme* lex) except -1


cdef English EN


cpdef LexID lookup(unicode word) except 0
cpdef Tokens tokenize(unicode string)
cpdef unicode unhash(StringHash hash_value)
