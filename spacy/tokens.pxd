cdef class Tokens:
    cdef list lexemes
    cpdef append(self, object lexeme)

    cpdef unicode string(self, size_t i)
    cpdef double prob(self, size_t i)
    cpdef size_t cluster(self, size_t i)
    cpdef bint check_flag(self, size_t i, size_t flag_id)
    cpdef unicode string_view(self, size_t i, size_t view_id)
