from spacy.spacy cimport Language
from spacy.lexeme cimport StringHash
from spacy.word cimport Word


cdef class PennTreebank3(Language):
    cpdef list find_substrings(self, unicode word)
    

cdef PennTreebank3 PTB3

cpdef Word lookup(unicode word)
cpdef list tokenize(unicode string)
cpdef unicode unhash(StringHash hash_value)
