from .typedefs cimport hash_t, utf8_t, flag_t, id_t
from spacy.lexeme cimport LexemeC

DEF MAX_FLAG = 64


cdef class Lexeme:
    cdef LexemeC* _c

    cpdef bint check_flag(self, size_t flag_id) except *
    cpdef unicode string_view(self, size_t view_id)
