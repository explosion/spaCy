from cymem.cymem cimport Pool

cdef class NERAnnotation:
    cdef Pool mem
    cdef int* starts
    cdef int* ends
    cdef int* labels
    cdef readonly list entities
