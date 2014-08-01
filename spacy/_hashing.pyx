from libc.stdlib cimport calloc, free
import cython


cdef class FixedTable:
    def __cinit__(self, const size_t size):
        self.size = size
        self.keys = <uint64_t*>calloc(self.size, sizeof(uint64_t))
        self.values = <size_t*>calloc(self.size, sizeof(size_t))

    def __dealloc__(self):
        free(self.keys)
        free(self.values)

    def __getitem__(self, uint64_t key):
        return self.get(key)

    def __setitem__(self, uint64_t key, size_t value):
        self.insert(key, value)

    def pop(self, uint64_t key):
        self.delete(key)

    def bucket(self, uint64_t key):
        return _find(key, self.size)

    cdef size_t insert(self, uint64_t key, size_t value) nogil:
        cdef size_t bucket = _find(key, self.size)
        cdef size_t clobbered
        if self.values[bucket] == value:
            clobbered = 0
        else:
            clobbered = self.values[clobbered]
        self.keys[bucket] = key
        self.values[bucket] = value
        return clobbered

    cdef size_t get(self, uint64_t key) nogil:
        cdef size_t bucket = _find(key, self.size)
        if self.keys[bucket] == key:
            return self.values[bucket]
        else:
            return 0

    cdef int erase(self, uint64_t key) nogil:
        cdef size_t bucket = _find(key, self.size)
        self.keys[bucket] = 0
        self.values[bucket] = 0


@cython.cdivision
cdef inline size_t _find(uint64_t key, size_t size) nogil:
    return key % size


