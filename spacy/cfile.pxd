from libc.stdio cimport fopen, fclose, fread, fwrite, FILE
from cymem.cymem cimport Pool

cdef class CFile:
    cdef FILE* fp
    cdef unsigned char* data
    cdef int is_open
    cdef Pool mem
    cdef int size # For compatibility with subclass
    cdef int i # For compatibility with subclass
    cdef int _capacity # For compatibility with subclass

    cdef int read_into(self, void* dest, size_t number, size_t elem_size) except -1

    cdef int write_from(self, void* src, size_t number, size_t elem_size) except -1

    cdef void* alloc_read(self, Pool mem, size_t number, size_t elem_size) except *



cdef class StringCFile:
    cdef unsigned char* data
    cdef int is_open
    cdef Pool mem
    cdef int size # For compatibility with subclass
    cdef int i # For compatibility with subclass
    cdef int _capacity # For compatibility with subclass
 
    cdef int read_into(self, void* dest, size_t number, size_t elem_size) except -1

    cdef int write_from(self, void* src, size_t number, size_t elem_size) except -1
    
    cdef void* alloc_read(self, Pool mem, size_t number, size_t elem_size) except *
