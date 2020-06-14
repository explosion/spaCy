from ..tokens.doc cimport Doc
from .align cimport Alignment


cdef class Example:
    cdef readonly Doc x
    cdef readonly Doc y
    cdef readonly Alignment _alignment
