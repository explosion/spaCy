cimport numpy as np

from .doc cimport Doc
from ..typedefs cimport attr_t


cdef class Span:
    cdef readonly Doc doc
    cdef readonly int start
    cdef readonly int end
    cdef readonly int start_char
    cdef readonly int end_char
    cdef readonly attr_t label
    cdef readonly attr_t kb_id

    cdef public _vector
    cdef public _vector_norm

    cpdef np.ndarray to_array(self, object features)
