from cymem.cymem cimport Pool
from preshed.maps cimport PreshMap
from murmurhash.mrmr cimport hash64

from .structs cimport Utf8Str, UniStr
from .typedefs cimport hash_t

cpdef hash_t hash_string(unicode string) except 0


cdef inline void slice_unicode(UniStr* s, Py_UNICODE* chars, int start, int end) nogil:
    s.chars = &chars[start]
    s.n = end - start
    s.key = hash64(s.chars, <int>(s.n * sizeof(Py_UNICODE)), 0)


cdef class StringStore:
    cdef Pool mem
    cdef Utf8Str* strings
    cdef size_t size

    cdef PreshMap _map
    cdef size_t _resize_at

    cdef const Utf8Str* intern(self, char* chars, int length) except NULL
