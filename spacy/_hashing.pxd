from libc.stdint cimport uint64_t

from chartree cimport CharTree


cdef class FixedTable:
    cdef size_t size
    cdef uint64_t* keys
    cdef size_t* values

    cdef size_t insert(self, uint64_t key, size_t value) nogil
    cdef size_t get(self, uint64_t key) nogil
    cdef int erase(self, uint64_t key) nogil


cdef class WordTree:
    cdef size_t max_length
    cdef size_t default
    cdef CharTree* _trees
    cdef dict _dict

    cdef size_t get(self, unicode string) except *
    cdef int set(self, unicode string, size_t value) except *
    cdef bint contains(self, unicode string) except *
    
