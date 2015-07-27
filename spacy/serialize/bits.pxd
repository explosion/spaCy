from libc.stdint cimport uint64_t
from libc.stdint cimport int32_t, uint32_t

ctypedef unsigned char uchar


cdef struct Code:
    uint64_t bits
    char length


cdef Code bit_append(Code code, bint bit) nogil


cdef class BitArray:
    cdef bytearray data
    cdef uchar byte
    cdef uchar bit_of_byte
    cdef uint32_t i
    
    cdef int extend(self, uint64_t code, char n_bits) except -1

    cpdef int32_t read32(self) except 0
