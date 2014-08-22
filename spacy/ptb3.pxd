from spacy.spacy cimport Language
from spacy.lexeme cimport LexID
from spacy.tokens cimport Tokens
from spacy.lexeme cimport StringHash


cdef class PennTreebank3(Language):
    cpdef list find_substrings(self, unicode word)
    

cdef PennTreebank3 PTB3

cpdef LexID lookup(unicode word) except 0
cpdef Tokens tokenize(unicode string)
cpdef unicode unhash(StringHash hash_value)
