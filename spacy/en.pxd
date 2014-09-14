from spacy.lang cimport Language
from spacy.word cimport Lexeme
from spacy.tokens cimport Tokens


cdef class English(Language):
    cdef int _split_one(self, Py_UNICODE* characters, size_t length)
