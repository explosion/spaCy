from __future__ import unicode_literals, absolute_import

cimport cython
from libc.string cimport memcpy
from libc.stdint cimport uint64_t

from murmurhash.mrmr cimport hash64

from preshed.maps cimport map_iter, key_t

from .typedefs cimport hash_t

try:
    import ujson as json
except ImportError:
    import json


cpdef hash_t hash_string(unicode string) except 0:
    chars = string.encode('utf8')
    return _hash_utf8(chars, len(chars))


cdef hash_t _hash_utf8(char* utf8_string, int length):
    return hash64(utf8_string, length, 1)


cdef unicode _decode(const Utf8Str* string):
    cdef int i, length
    if string.s[0] < sizeof(string.s) and string.s[0] != 0:
        return string.s[1:string.s[0]+1].decode('utf8')
    elif string.p[0] < 255:
        return string.p[1:string.p[0]+1].decode('utf8')
    else:
        i = 0
        length = 0
        while string.p[i] == 255:
            i += 1
            length += 255
        length += string.p[i]
        i += 1
        return string.p[i:length + i].decode('utf8')


cdef Utf8Str _allocate(Pool mem, const unsigned char* chars, int length) except *:
    cdef int n_length_bytes
    cdef int i
    cdef Utf8Str string
    assert length != 0
    if length < sizeof(string.s):
        string.s[0] = <unsigned char>length
        memcpy(&string.s[1], chars, length)
        return string
    elif length < 255:
        string.p = <unsigned char*>mem.alloc(length + 1, sizeof(unsigned char))
        string.p[0] = length
        memcpy(&string.p[1], chars, length)
        assert string.s[0] >= sizeof(string.s) or string.s[0] == 0, string.s[0]
        return string
    else:
        i = 0
        n_length_bytes = (length // 255) + 1
        string.p = <unsigned char*>mem.alloc(length + n_length_bytes, sizeof(unsigned char))
        for i in range(n_length_bytes-1):
            string.p[i] = 255
        string.p[n_length_bytes-1] = length % 255
        memcpy(&string.p[n_length_bytes], chars, length)
        assert string.s[0] >= sizeof(string.s) or string.s[0] == 0, string.s[0]
        return string


cdef class StringStore:
    '''Map strings to and from integer IDs.'''
    def __init__(self, strings=None):
        self.mem = Pool()
        self._map = PreshMap()
        self._resize_at = 10000
        self.c = <Utf8Str*>self.mem.alloc(self._resize_at, sizeof(Utf8Str))
        self.size = 1
        if strings is not None:
            for string in strings:
                _ = self[string]

    property size:
        def __get__(self):
            return self.size -1

    def __len__(self):
        return self.size-1

    def __getitem__(self, object string_or_id):
        cdef bytes byte_string
        cdef const Utf8Str* utf8str
        cdef unsigned int int_id

        if isinstance(string_or_id, (int, long)):
            try:
                int_id = string_or_id
            except OverflowError:
                raise IndexError(string_or_id)
            if int_id == 0:
                return u''
            elif int_id >= <uint64_t>self.size:
                raise IndexError(string_or_id)
            utf8str = &self.c[int_id]
            return _decode(utf8str)
        elif isinstance(string_or_id, bytes):
            byte_string = <bytes>string_or_id
            if len(byte_string) == 0:
                return 0
            utf8str = self._intern_utf8(byte_string, len(byte_string))
            return utf8str - self.c
        elif isinstance(string_or_id, unicode):
            if len(<unicode>string_or_id) == 0:
                return 0
            byte_string = (<unicode>string_or_id).encode('utf8')
            utf8str = self._intern_utf8(byte_string, len(byte_string))
            return utf8str - self.c
        else:
            raise TypeError(type(string_or_id))

    def __contains__(self, unicode string not None):
        if len(string) == 0:
            return True
        cdef hash_t key = hash_string(string)
        return self._map.get(key) is not NULL

    def __iter__(self):
        cdef int i
        for i in range(self.size):
            yield _decode(&self.c[i]) if i > 0 else u''

    def __reduce__(self):
        strings = [""]
        for i in range(1, self.size):
            string = &self.c[i]
            py_string = _decode(string)
            strings.append(py_string)
        return (StringStore, (strings,), None, None, None)

    cdef const Utf8Str* intern(self, unicode py_string) except NULL:
        # 0 means missing, but we don't bother offsetting the index.
        cdef bytes byte_string = py_string.encode('utf8')
        return self._intern_utf8(byte_string, len(byte_string))

    @cython.final
    cdef const Utf8Str* _intern_utf8(self, char* utf8_string, int length) except NULL:
        # 0 means missing, but we don't bother offsetting the index.
        cdef hash_t key = _hash_utf8(utf8_string, length)
        value = <Utf8Str*>self._map.get(key)
        if value is not NULL:
            return value

        if self.size == self._resize_at:
            self._realloc()
        self.c[self.size] = _allocate(self.mem, <unsigned char*>utf8_string, length)
        self._map.set(key, <void*>&self.c[self.size])
        self.size += 1
        return &self.c[self.size-1]

    def dump(self, file_):
        string_data = json.dumps(list(self))
        if not isinstance(string_data, unicode):
            string_data = string_data.decode('utf8')
        file_.write(string_data)

    def load(self, file_):
        strings = json.load(file_)
        if strings == ['']:
            return None
        cdef unicode string
        for string in strings:
            # explicit None/len check instead of simple truth testing
            # (bug in Cython <= 0.23.4)
            if string is not None and len(string):
                self.intern(string)

    def _realloc(self):
        # We want to map straight to pointers, but they'll be invalidated if
        # we resize our array. So, first we remap to indices, then we resize,
        # then we can acquire the new pointers.
        cdef Pool tmp_mem = Pool()
        keys = <key_t*>tmp_mem.alloc(self.size, sizeof(key_t))
        cdef key_t key
        cdef void* value
        cdef const Utf8Str ptr
        cdef int i = 0
        cdef size_t offset
        while map_iter(self._map.c_map, &i, &key, &value):
            # Find array index with pointer arithmetic
            offset = ((<Utf8Str*>value) - self.c)
            keys[offset] = key
        
        self._resize_at *= 2
        cdef size_t new_size = self._resize_at * sizeof(Utf8Str)
        self.c = <Utf8Str*>self.mem.realloc(self.c, new_size)

        self._map = PreshMap(self.size)
        for i in range(self.size):
            if keys[i]:
                self._map.set(keys[i], &self.c[i])
