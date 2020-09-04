from libc.stdint cimport int64_t
from libcpp.vector cimport vector
from libcpp.set cimport set
from cymem.cymem cimport Pool
from preshed.maps cimport PreshMap
from murmurhash.mrmr cimport hash64

from .typedefs cimport attr_t, hash_t


cpdef hash_t hash_string(unicode string) except 0
cdef hash_t hash_utf8(char* utf8_string, int length) nogil

cdef unicode decode_Utf8Str(const Utf8Str* string)


ctypedef union Utf8Str:
    unsigned char[8] s
    unsigned char* p


cdef class StringStore:
    cdef Pool mem

    cdef vector[hash_t] keys
    cdef public PreshMap _map

    cdef const Utf8Str* intern_unicode(self, unicode py_string)
    cdef const Utf8Str* _intern_utf8(self, char* utf8_string, int length)
