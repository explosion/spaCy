from .typedefs cimport hash_t, utf8_t, flag_t, id_t


DEF MAX_FLAG = 64


cdef class Lexeme:
    # NB: the readonly keyword refers to _Python_ access. The attributes are
    # writeable from Cython.
    cdef readonly id_t id
    cdef readonly size_t length
    cdef readonly double prob
    cdef readonly size_t cluster

    cdef readonly utf8_t* strings
    cdef readonly size_t nr_strings

    cdef readonly flag_t flags

    cpdef bint check_flag(self, size_t flag_id) except *
    cpdef int set_flag(self, size_t flag_id) except -1
    
    cpdef unicode get_string(self, size_t i) except *
    cpdef id_t get_id(self, size_t i) except 0
    cpdef int add_strings(self, list strings) except -1
