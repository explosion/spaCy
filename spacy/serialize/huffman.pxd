from libcpp.vector cimport vector
from libc.stdint cimport uint32_t
from libc.stdint cimport int64_t
from libc.stdint cimport int32_t
from libc.stdint cimport uint64_t

from .bits cimport BitArray, Code


cdef struct Node:
    int32_t left
    int32_t right


cdef class HuffmanCodec:
    cdef vector[Node] nodes
    cdef vector[Code] codes
    cdef Node root

    cdef readonly list leaves
    cdef readonly dict _map 
    
    cpdef int encode_int32(self, int32_t[:] msg, BitArray bits) except -1
    cpdef int decode_int32(self, BitArray bits, int32_t[:] msg) except -1
