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


cdef bytes to_utf8(unicode string):
    cdef bytes py_byte_string = string.encode('UTF-8')
    return py_byte_string


cdef unicode to_unicode(unsigned char[:] c_string, size_t length):
    # This prevents a call to strlen
    cdef bytes py_string = <bytes>c_string[:length]
    return py_string.decode('utf8')


cdef class WordTree:
    def __cinit__(self, size_t default, size_t max_length):
        self.max_length = max_length
        self.default = default
        self._trees = <CharTree*>calloc(max_length, sizeof(CharTree))
        for i in range(self.max_length):
            chartree.init(&self._trees[i], i)
        self._dict = {}

    cdef size_t get(self, bytes string) except *:
        cdef size_t length = len(string)
        if length >= self.max_length:
            return self._dict.get(string, 0)
        else:
            return chartree.getitem(&self._trees[length], string)

    cdef int set(self, bytes string, size_t value) except *:
        cdef size_t length = len(string)
        if length >= self.max_length:
            self._dict[string] = value
        else:
            chartree.setitem(&self._trees[length], string, value)

    cdef bint contains(self, bytes string) except *:
        cdef size_t length = len(string)
        if length >= self.max_length:
            return string in self._dict
        else:
            return chartree.contains(&self._trees[length], string)

    def __getitem__(self, unicode key):
        return self.get(to_utf8(key))

    def __setitem__(self, unicode key, size_t value):
        self.set(to_utf8(key), value)
    
    def __contains__(self, unicode key):
        return self.contains(to_utf8(key))
