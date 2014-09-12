from spacy.lexeme cimport LexemeC

cdef class Tokens:
    cdef size_t length
    cdef size_t size

    cdef LexemeC** lexemes
    cdef int push_back(self, LexemeC* lexeme) except -1

    cpdef unicode string(self, size_t i)
    cpdef double prob(self, size_t i)
    cpdef size_t cluster(self, size_t i)
    cpdef bint check_flag(self, size_t i, size_t flag_id)
    cpdef unicode string_view(self, size_t i, size_t view_id)
