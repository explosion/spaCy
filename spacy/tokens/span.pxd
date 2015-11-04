from .doc cimport Doc


cdef class Span:
    cdef readonly Doc doc
    cdef public int i
    cdef public int start_token
    cdef public int end_token
    cdef public int start_idx
    cdef public int end_idx
    cdef readonly int label

    cdef public _vector
    cdef public _vector_norm
