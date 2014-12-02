from preshed.maps cimport PreshMap
from cymem.cymem cimport Pool

from .typedefs cimport utf8_t, id_t, hash_t


cdef struct Utf8Str:
    id_t i
    hash_t key
    utf8_t chars
    int length


cdef class StringStore:
    cdef Pool mem
    cdef PreshMap _map
    cdef Utf8Str* strings
    cdef int size
    cdef int _resize_at
    
    cdef Utf8Str* intern(self, char* chars, int length) except NULL
