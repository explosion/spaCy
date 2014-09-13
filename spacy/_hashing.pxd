from libc.stdint cimport uint64_t

ctypedef uint64_t key_t
ctypedef void* val_t


cdef struct Cell:
    key_t key
    val_t value


cdef class PointerHash:
    cdef size_t size
    cdef size_t filled
    cdef Cell* _last
    cdef Cell* cells

    cdef val_t get(self, key_t key)
    cdef void set(self, key_t key, val_t value) except *
    cdef void resize(self, size_t new_size) except *
