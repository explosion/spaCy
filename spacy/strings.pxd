from cymem.cymem cimport Pool
from libc.stdint cimport int64_t, uint32_t
from libcpp.set cimport set
from libcpp.vector cimport vector
from murmurhash.mrmr cimport hash64
from preshed.maps cimport PreshMap

from .typedefs cimport attr_t, hash_t

ctypedef union Utf8Str:
    unsigned char[8] s
    unsigned char* p


cdef class StringStore:
    cdef Pool mem
    cdef vector[hash_t] _keys
    cdef PreshMap _map

    cdef hash_t _intern_str(self, str string)
    cdef Utf8Str* _allocate_str_repr(self, const unsigned char* chars, uint32_t length) except *
    cdef str _decode_str_repr(self, const Utf8Str* string)


cpdef hash_t hash_string(object string) except -1
cpdef hash_t get_string_id(object string_or_hash) except -1
