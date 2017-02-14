from libcpp.vector cimport vector
from spacy.strings cimport StringStore
from murmurhash.mrmr cimport hash64

from cymem.cymem cimport Pool


cdef class VectorStore:
    cdef readonly Pool mem
    cdef vector[float*] vectors
    cdef vector[float] norms
    cdef readonly int nr_dim


cdef class VectorMap:
    cdef readonly Pool mem
    cdef readonly VectorStore data
    cdef readonly StringStore strings
