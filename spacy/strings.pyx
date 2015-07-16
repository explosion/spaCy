import codecs

from libc.string cimport memcpy
from murmurhash.mrmr cimport hash64


from .typedefs cimport hash_t


SEPARATOR = '\n|-SEP-|\n'


cpdef hash_t hash_string(unicode string) except 0:
    chars = <Py_UNICODE*>string
    return hash64(chars, len(string) * sizeof(Py_UNICODE), 0)


cdef class StringStore:
    '''Map strings to and from integer IDs.'''
    def __init__(self):
        self.mem = Pool()
        self._map = PreshMap()
        self._resize_at = 10000
        self.strings = <Utf8Str*>self.mem.alloc(self._resize_at, sizeof(Utf8Str))
        self.size = 1

    property size:
        def __get__(self):
            return self.size-1

    def __len__(self):
        return self.size

    def __getitem__(self, object string_or_id):
        cdef bytes byte_string
        cdef const Utf8Str* utf8str
        if isinstance(string_or_id, int) or isinstance(string_or_id, long):
            if string_or_id == 0:
                return u''
            elif string_or_id < 1 or string_or_id >= self.size:
                raise IndexError(string_or_id)
            utf8str = &self.strings[<int>string_or_id]
            return utf8str.chars[:utf8str.length].decode('utf8')
        elif isinstance(string_or_id, bytes):
            utf8str = self.intern(<char*>string_or_id, len(string_or_id))
            return utf8str.i
        elif isinstance(string_or_id, unicode):
            byte_string = string_or_id.encode('utf8')
            utf8str = self.intern(<char*>byte_string, len(byte_string))
            return utf8str.i
        else:
            raise TypeError(type(string_or_id))

    cdef const Utf8Str* intern(self, char* chars, int length) except NULL:
        # 0 means missing, but we don't bother offsetting the index. We waste
        # slot 0 to simplify the code, because it doesn't matter.
        assert length != 0
        cdef hash_t key = hash64(chars, length * sizeof(char), 0)
        cdef void* value = self._map.get(key)
        cdef size_t i
        if value == NULL:
            if self.size == self._resize_at:
                self._resize_at *= 2
                self.strings = <Utf8Str*>self.mem.realloc(self.strings, self._resize_at * sizeof(Utf8Str))
            i = self.size
            self.strings[i].i = self.size
            self.strings[i].key = key
            self.strings[i].chars = <unsigned char*>self.mem.alloc(length, sizeof(char))
            memcpy(self.strings[i].chars, chars, length)
            self.strings[i].length = length
            self._map.set(key, <void*>self.size)
            self.size += 1
        else:
            i = <size_t>value
        return &self.strings[i]

    def dump(self, loc):
        cdef Utf8Str* string
        cdef bytes py_string
        cdef int i
        with codecs.open(loc, 'w', 'utf8') as file_:
            for i in range(self.size):
                string = &self.strings[i]
                py_string = string.chars[:string.length]
                file_.write(py_string.decode('utf8'))
                file_.write(SEPARATOR)

    def load(self, loc):
        with codecs.open(loc, 'r', 'utf8') as file_:
            strings = file_.read().split(SEPARATOR)
        cdef unicode string
        cdef bytes byte_string
        for string in strings[1:]:
            byte_string = string.encode('utf8')
            self.intern(byte_string, len(byte_string))
