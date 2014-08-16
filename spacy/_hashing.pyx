from libc.stdlib cimport calloc, free
import cython

cimport chartree


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
            clobbered = self.values[bucket]
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


cdef class WordTree:
    def __cinit__(self, size_t default, size_t max_length):
        self.max_length = max_length
        self.default = default
        self._trees = <CharTree*>calloc(max_length, sizeof(CharTree))
        for i in range(self.max_length):
            chartree.init(&self._trees[i], i)
        self._dict = {}

    cdef size_t get(self, unicode ustring) except *:
        cdef bytes bstring = ustring.encode('utf8')
        cdef size_t length = len(bstring)
        if length >= self.max_length:
            return self._dict.get(bstring, 0)
        else:
            return chartree.getitem(&self._trees[length], bstring)

    cdef int set(self, unicode ustring, size_t value) except *:
        cdef bytes bstring = ustring.encode('utf8')
        cdef size_t length = len(bstring)
        if length >= self.max_length:
            self._dict[bstring] = value
        else:
            chartree.setitem(&self._trees[length], bstring, value)

    cdef bint contains(self, unicode ustring) except *:
        cdef bytes bstring = ustring.encode('utf8')
        cdef size_t length = len(bstring)
        if length >= self.max_length:
            return bstring in self._dict
        else:
            return chartree.contains(&self._trees[length], bstring)

    def __getitem__(self, unicode key):
        return self.get(key)

    def __setitem__(self, unicode key, size_t value):
        self.set(key, value)
    
    def __contains__(self, unicode key):
        return self.contains(key)
