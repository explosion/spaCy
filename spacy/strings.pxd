from cymem.cymem cimport Pool
from preshed.maps cimport PreshMap

from .structs cimport Utf8Str


cdef class StringStore:
    cdef Pool mem
    cdef Utf8Str* strings
    cdef size_t size

    cdef PreshMap _map
    cdef size_t _resize_at

    cdef const Utf8Str* intern(self, char* chars, int length) except NULL
