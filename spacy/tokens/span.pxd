cimport numpy as np
from libcpp.memory cimport shared_ptr

from ..structs cimport SpanC
from ..typedefs cimport attr_t
from .doc cimport Doc


cdef class Span:
    cdef readonly Doc doc
    cdef shared_ptr[SpanC] c
    cdef public _vector
    cdef public _vector_norm

    @staticmethod
    cdef inline Span cinit(Doc doc, const shared_ptr[SpanC] &span):
        cdef Span self = Span.__new__(
            Span,
            doc,
            start=span.get().start,
            end=span.get().end
        )
        self.c = span
        return self

    cpdef np.ndarray to_array(self, object features)

    cdef SpanC* span_c(self)
