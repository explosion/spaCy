from ..tokens.doc cimport Doc


cdef class Example:
    cdef readonly Doc x
    cdef readonly Doc y
    cdef readonly object _alignment
