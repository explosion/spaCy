from cpython.mem cimport PyMem_Malloc, PyMem_Realloc, PyMem_Free
from libc.string cimport memset

from libcpp.vector cimport vector

from cymem cimport Pool


cdef class Pool:
    def __cinit__(self):
        pass

    def __dealloc__(self):
        cdef void* addr
        for addr in self._addresses:
            PyMem_Free(<void*>addr)

    cdef void* alloc(self, size_t number, size_t size) except NULL:
        cdef void* addr = PyMem_Malloc(number * size)
        memset(addr, 0, number * size)
        self._addresses.push_back(addr)
        return addr

    cdef void* realloc(self, void* addr, size_t n) except NULL:
        cdef size_t i
        for i in range(self.size()):
            if self._addresses[i] == addr:
                self._addresses[i] = PyMem_Realloc(addr, n)
                return self._addresses[i]
        else:
            raise MemoryError("Address to realloc not found in pool")


cdef class Address:
    def __cinit__(self, size_t number, size_t size):
        cdef void* addr = PyMem_Malloc(number * size)
        memset(addr, 0, number * size)
        self.addr = <size_t>addr

    def __dealloc__(self):
        PyMem_Free(<void*>self.addr)
