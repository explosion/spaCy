from libcpp.vector cimport vector
from cymem.cymem cimport Pool
from preshed.maps cimport PreshMap
from ..structs cimport GraphC, EdgeC


cdef class Graph:
    cdef GraphC c
    cdef Pool mem
    cdef PreshMap node_map
    cdef PreshMap edge_map
    cdef object doc_ref
    cdef public str name
