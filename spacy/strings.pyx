import codecs

from libc.string cimport memcpy
from murmurhash.mrmr cimport hash64

from libc.stdint cimport int64_t


from .typedefs cimport hash_t, attr_t


SEPARATOR = '\n|-SEP-|\n'


cpdef hash_t hash_string(unicode string) except 0:
    chars = <Py_UNICODE*>string
    return hash64(chars, len(string) * sizeof(Py_UNICODE), 0)


cdef unicode _decode(const Utf8Str* string):
    if string.s[0] < sizeof(string.s) and string.s[0] != 0:
        return string.s[1:string.s[0]+1].decode('utf8')
    elif string.p[0] < 256:
        return string.p[1:string.p[0]+1].decode('utf8')
    else:
        raise Exception(string.p[0])
    cdef int i = 0
    cdef int length = 0
    while string.p[i] == 255:
        i += 1
        length += 255
    length += string.p[i]
    i += 1
    return string.p[i:length - i].decode('utf8')


cdef Utf8Str _allocate(Pool mem, const unsigned char* chars, int length) except *:
    cdef Utf8Str string
    assert length != 0
    if length < sizeof(string.s):
        string.s[0] = <unsigned char>length
        memcpy(&string.s[1], chars, length)
        return string
    elif length < 256:
        string.p = <unsigned char*>mem.alloc(length + 1, sizeof(unsigned char))
        string.p[0] = length
        memcpy(&string.p[1], chars, length)
        assert string.s[0] >= sizeof(string.s) or string.s[0] == 0, string.s[0]
        return string
    else:
        raise Exception(length)
    cdef int n_length_bytes = (length // 256) + ((length % 256) != 0)
    cdef int i = 0
    while length >= 256:
        string.p[i] = 255
        length -= 255
        i += 1
    string.p[i] = length
    memcpy(&string.p[i+1], chars, length)
    return string


cdef class StringStore:
    '''Map strings to and from integer IDs.'''
    def __init__(self):
        self.mem = Pool()
        self._map = PreshMap()
        self._resize_at = 10000
        self.c = <Utf8Str*>self.mem.alloc(self._resize_at, sizeof(Utf8Str))
        self.size = 1

    property size:
        def __get__(self):
            return self.size -1

    def __len__(self):
        return self.size-1

    def __getitem__(self, object string_or_id):
        cdef bytes byte_string
        cdef const Utf8Str* utf8str
        if isinstance(string_or_id, int) or isinstance(string_or_id, long):
            if string_or_id == 0:
                return u''
            elif string_or_id < 1 or string_or_id >= self.size:
                raise IndexError(string_or_id)
            utf8str = &self.c[<int>string_or_id]
            return _decode(utf8str)
        elif isinstance(string_or_id, bytes):
            utf8str = self.intern(<unsigned char*>string_or_id, len(string_or_id))
            return utf8str - self.c
        elif isinstance(string_or_id, unicode):
            byte_string = string_or_id.encode('utf8')
            utf8str = self.intern(<unsigned char*>byte_string, len(byte_string))
            return utf8str - self.c
        else:
            raise TypeError(type(string_or_id))

    cdef const Utf8Str* intern(self, unsigned char* chars, int length) except NULL:
        # 0 means missing, but we don't bother offsetting the index.
        key = hash64(chars, length * sizeof(char), 0)
        value = <Utf8Str*>self._map.get(key)
        if value != NULL:
            return value

        if self.size == self._resize_at:
            self._realloc()
        self.c[self.size] = _allocate(self.mem, chars, length)
        self._map.set(key, <void*>&self.c[self.size])
        self.size += 1
        return &self.c[self.size-1]

    def dump(self, loc):
        cdef Utf8Str* string
        cdef unicode py_string
        cdef int i
        with codecs.open(loc, 'w', 'utf8') as file_:
            for i in range(1, self.size):
                string = &self.c[i]
                py_string = _decode(string)
                file_.write(py_string.decode('utf8'))
                if (i+1) != self.size:
                    file_.write(SEPARATOR)

    def load(self, loc):
        with codecs.open(loc, 'r', 'utf8') as file_:
            strings = file_.read().split(SEPARATOR)
        cdef unicode string
        cdef bytes byte_string
        for string in strings: 
            byte_string = string.encode('utf8')
            self.intern(byte_string, len(byte_string))

    def _realloc(self):
        # We want to map straight to pointers, but they'll be invalidated if
        # we resize our array. So, first we remap to indices, then we resize,
        # then we can acquire the new pointers.
        cdef Pool tmp_mem = Pool()
        keys = <hash_t*>tmp_mem.alloc(self.size, sizeof(hash_t))
        cdef hash_t key
        cdef size_t addr
        cdef const Utf8Str ptr
        cdef size_t i
        for key, addr in self._map.items():
            # Find array index with pointer arithmetic
            i = (<Utf8Str*>addr) - self.c
            keys[i] = key
        
        self._resize_at *= 2
        cdef size_t new_size = self._resize_at * sizeof(Utf8Str)
        self.c = <Utf8Str*>self.mem.realloc(self.c, new_size)

        self._map = PreshMap(self.size)
        for i in range(self.size):
            self._map.set(keys[i], &self.c[i])
