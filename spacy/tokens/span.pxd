from .doc cimport Doc


cdef class Span:
    cdef readonly Doc doc
    cdef public int i
    cdef public int start
    cdef public int end
    cdef public int start_char
    cdef public int end_char
    cdef readonly int label

    cdef public _vector
    cdef public _vector_norm
