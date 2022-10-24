"""Knowledge-base for entity or concept linking."""

from cymem.cymem cimport Pool
from libc.stdint cimport int64_t
from ..vocab cimport Vocab

cdef class KnowledgeBase:
    cdef Pool mem
    cdef readonly Vocab vocab
    cdef readonly int64_t entity_vector_length
