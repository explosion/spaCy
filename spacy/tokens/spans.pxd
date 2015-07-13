from .doc cimport Doc


cdef class Span:
    cdef readonly Doc _seq
    cdef public int i
    cdef public int start
    cdef public int end
    cdef readonly int label
