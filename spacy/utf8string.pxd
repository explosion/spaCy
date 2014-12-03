from preshed.maps cimport PreshMap
from cymem.cymem cimport Pool
from murmurhash.mrmr cimport hash64

from .typedefs cimport utf8_t, id_t, hash_t


cdef struct Utf8Str:
    id_t i
    hash_t key
    utf8_t chars
    int length


cdef struct UniStr:
    Py_UNICODE* chars
    size_t n
    hash_t key


cdef inline void slice_unicode(UniStr* s, Py_UNICODE* chars, int start, int end) nogil:
    s.chars = &chars[start]
    s.n = end - start
    s.key = hash64(s.chars, s.n * sizeof(Py_UNICODE), 0)


cdef class StringStore:
    cdef Pool mem
    cdef PreshMap _map
    cdef Utf8Str* strings
    cdef int size
    cdef int _resize_at
    
    cdef Utf8Str* intern(self, char* chars, int length) except NULL
