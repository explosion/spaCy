from libcpp.vector cimport vector

from spacy.spacy cimport StringHash

from spacy.spacy cimport Language
from spacy.word cimport Word
from spacy.tokens cimport Tokens
cimport cython


cdef class English(spacy.Language):
    cdef int find_split(self, unicode word)
    cdef int set_orth(self, unicode word, Word lex) except -1


cdef English EN


cpdef Word lookup(unicode word)
cpdef list tokenize(unicode string)
cpdef unicode unhash(StringHash hash_value)
