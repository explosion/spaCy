cimport numpy as np

from .doc cimport Doc
from ..typedefs cimport attr_t
from ..structs cimport SpanC


cdef class Span:
    cdef readonly Doc doc
    cdef SpanC c
    cdef public _vector
    cdef public _vector_norm

    @staticmethod
    cdef inline Span cinit(Doc doc, SpanC span):
        cdef Span self = Span.__new__(
            Span,
            doc,
            start=span.start,
            end=span.end
        )
        self.c = span
        return self

    cpdef np.ndarray to_array(self, object features)
