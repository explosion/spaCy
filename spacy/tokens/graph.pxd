from cymem.cymem cimport Pool
from libcpp.vector cimport vector
from preshed.maps cimport PreshMap

from ..structs cimport EdgeC, GraphC


cdef class Graph:
    cdef GraphC c
    cdef Pool mem
    cdef PreshMap node_map
    cdef PreshMap edge_map
    cdef object doc_ref
    cdef public str name
