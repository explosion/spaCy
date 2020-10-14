from ..tokens.doc cimport Doc
from libc.stdint cimport uint64_t


cdef class Example:
    cdef readonly Doc x
    cdef readonly Doc y
    cdef readonly object _cached_alignment
    cdef readonly object _cached_words_x
    cdef readonly object _cached_words_y
    cdef readonly uint64_t _x_sig
    cdef readonly uint64_t _y_sig
