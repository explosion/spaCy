from libc.stdint cimport uint64_t


cdef class FixedTable:
    cdef size_t size
    cdef uint64_t* keys
    cdef size_t* values

    cdef size_t insert(self, uint64_t key, size_t value) nogil
    cdef size_t get(self, uint64_t key) nogil
    cdef int erase(self, uint64_t key) nogil
