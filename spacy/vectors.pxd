from libcpp.vector cimport vector
from preshed.maps cimport PreshMap
from spacy.strings cimport StringStore, hash_string
from murmurhash.mrmr cimport hash64

from cymem.cymem cimport Pool


cdef class VectorStore:
    cdef readonly Pool mem
    cdef readonly PreshMap cache
    cdef vector[float*] vectors
    cdef vector[float] norms
    cdef vector[float] _similarities
    cdef readonly int nr_dim

cdef class VectorMap:
    cdef readonly Pool mem
    cdef readonly VectorStore data
    cdef readonly StringStore strings
    cdef readonly PreshMap freqs
