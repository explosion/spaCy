from ..tokens.doc cimport Doc


cdef class Example:
    cdef readonly Doc x
    cdef readonly Doc y
    cdef readonly object _cached_alignment
    cdef readonly object _cached_words_x
    cdef readonly object _cached_words_y
