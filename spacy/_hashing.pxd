from libc.stdint cimport uint64_t

ctypedef uint64_t key_t
ctypedef size_t val_t


cdef struct Cell:
    key_t key
    val_t value


cdef class PointerHash:
    cdef size_t size
    cdef size_t filled
    cdef Cell* cells

    cdef size_t find_slot(self, key_t key)
    cdef Cell* lookup(self, key_t key)
    cdef void insert(self, key_t key, val_t value)
    cdef void resize(self, size_t new_size)
