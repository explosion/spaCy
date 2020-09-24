from ..tokens.doc cimport Doc
from murmurhash.mrmr cimport hash_t


cdef class Example:
    cdef readonly Doc x
    cdef readonly Doc y
    cdef readonly object _cached_alignment
    cdef readonly object _cached_words_x
    cdef readonly object _cached_words_y
    cdef readonly hash_t _x_sig
    cdef readonly hash_t _y_sig
