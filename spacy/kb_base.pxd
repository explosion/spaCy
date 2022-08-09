"""Knowledge-base for entity or concept linking."""

from cymem.cymem cimport Pool
from libcpp.vector cimport vector
from libc.stdint cimport int64_t

from .vocab cimport Vocab
from .typedefs cimport hash_t
from .kb_base cimport BaseKnowledgeBase


# Object used by the Entity Linker that summarizes one entity-alias candidate combination.
cdef class Candidate:
    cdef readonly BaseKnowledgeBase kb
    cdef hash_t entity_hash
    cdef float entity_freq
    cdef vector[float] entity_vector
    cdef hash_t alias_hash
    cdef float prior_prob


cdef class BaseKnowledgeBase:
    cdef Pool mem
    cdef readonly Vocab vocab
    cdef readonly int64_t entity_vector_length
