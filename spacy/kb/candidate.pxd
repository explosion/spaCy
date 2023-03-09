from libcpp.vector cimport vector
from .kb_in_memory cimport InMemoryLookupKB
from ..typedefs cimport hash_t

cdef class Candidate:
    cdef readonly str _entity_id_
    cdef readonly hash_t _entity_id
    cpdef vector[float] _entity_vector
    cdef float _prior_prob


cdef class InMemoryCandidate(Candidate):
    cdef readonly InMemoryLookupKB _kb
    cdef hash_t _entity_hash
    cdef float _entity_freq
    cdef hash_t _mention
