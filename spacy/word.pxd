from .typedefs cimport hash_t, utf8_t, flag_t, id_t


DEF MAX_FLAG = 64


cdef class Lexeme:
    # NB: the readonly keyword refers to _Python_ access. The attributes are
    # writeable from Cython.
    cpdef readonly id_t id
    cpdef readonly size_t length
    cpdef readonly double prob
    cpdef readonly size_t cluster

    cdef utf8_t* views
    cdef size_t nr_views

    cdef readonly flag_t flags

    cpdef bint check_flag(self, size_t flag_id) except *
    cpdef int set_flag(self, size_t flag_id) except -1
    
    cpdef unicode get_view_string(self, size_t i)
    cpdef id_t get_view_id(self, size_t i) except 0
    cpdef int add_view(self, unicode view) except -1
