from ..tokens.doc cimport Doc
from .align cimport Alignment


cdef class NewExample:
    cdef readonly Doc x
    cdef readonly Doc y
    cdef readonly Alignment _alignment
