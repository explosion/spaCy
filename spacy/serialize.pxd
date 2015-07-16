from libcpp.vector cimport vector
from libc.stdint cimport uint32_t
from libc.stdint cimport int64_t
from libc.stdint cimport int32_t
from libc.stdint cimport uint64_t


cdef struct Node:
    float prob
    int32_t left
    int32_t right


cdef struct Code:
    uint64_t bits
    char length


cdef class Serializer:
    cdef list codecs


cdef class HuffmanCodec:
    cdef vector[Node] nodes
    cdef vector[Code] codes
    cdef uint32_t eol
    cdef int id

