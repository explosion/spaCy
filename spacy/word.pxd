from .typedefs cimport hash_t, utf8_t, flag_t, id_t


DEF MAX_FLAG = 64


cdef class Lexeme:
    # NB: the readonly keyword refers to _Python_ access. The attributes are
    # writeable from Cython.
    cpdef readonly size_t length
    cpdef readonly double prob
    cpdef readonly size_t cluster

    cpdef readonly unicode string
    cpdef readonly list views

    cdef readonly flag_t flags

    cpdef bint check_flag(self, size_t flag_id) except *
    cpdef unicode string_view(self, size_t view_id)
