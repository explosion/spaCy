from libcpp.vector cimport vector

from ..typedefs cimport hash_t
from .kb_in_memory cimport InMemoryLookupKB


cdef class Candidate:
    pass


cdef class InMemoryCandidate(Candidate):
    cdef readonly hash_t _entity_hash
    cdef readonly hash_t _alias_hash
    cdef vector[float] _entity_vector
    cdef float _prior_prob
    cdef readonly InMemoryLookupKB _kb
    cdef float _entity_freq
