from libcpp.vector cimport vector
#from ..structs cimport SpanC
from .span cimport Span

cdef class SpanGroup:
    cdef public object _doc_ref
    cdef public str name
    cdef public dict attrs
    #cdef vector[SpanC] c
    cdef list spans

    #cdef void push_back(self, SpanC span) nogil
