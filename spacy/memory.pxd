from libcpp.vector cimport vector
from cymem.cymem cimport Pool

cdef class _Pool:
    cdef vector[void*] _addresses

    cdef void* alloc(self, size_t number, size_t size) except NULL
    cdef void* realloc(self, void* addr, size_t n) except NULL


cdef class Address:
    cdef size_t addr
