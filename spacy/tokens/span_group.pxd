from libcpp.memory cimport shared_ptr
from libcpp.vector cimport vector
from ..structs cimport SpanC

cdef class SpanGroup:
    cdef public object _doc_ref
    cdef public str name
    cdef public dict attrs
    cdef vector[shared_ptr[SpanC]] c

    cdef void push_back(self, const shared_ptr[SpanC] &span)
