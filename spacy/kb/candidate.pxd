from libcpp.vector cimport vector
from .kb_in_memory cimport InMemoryLookupKB
from ..typedefs cimport hash_t

cdef class Candidate:
    pass


cdef class InMemoryCandidate(Candidate):
    cdef readonly hash_t _entity_hash
    cdef readonly hash_t _alias_hash
    cpdef vector[float] _entity_vector
    cdef float _prior_prob
    cdef readonly InMemoryLookupKB _kb
    cdef float _entity_freq
