import numpy as np
cimport numpy as np

from cymem.cymem cimport Pool
from thinc.typedefs cimport atom_t

from .lexeme cimport Lexeme

from .typedefs cimport flags_t
from .utf8string cimport StringStore
from libc.stdint cimport uint8_t, uint16_t


cdef struct Morphology:
    uint8_t number
    uint8_t tenspect # Tense/aspect/voice
    uint8_t mood
    uint8_t gender
    uint8_t person
    uint8_t case
    uint8_t misc


cdef struct TokenC:
    const Lexeme* lex
    Morphology morph
    int idx
    int pos
    int lemma
    int sense


cdef class Tokens:
    cdef Pool mem
    cdef StringStore _string_store

    cdef TokenC* data

    cdef int length
    cdef int max_length

    cdef int extend(self, int i, const Lexeme* const* lexemes, int n) except -1
    cdef int push_back(self, int i, const Lexeme* lexeme) except -1
    cpdef int set_tag(self, int i, int tag_type, int tag) except -1

    cpdef np.ndarray[long, ndim=2] get_array(self, list features)


cdef class Token:
    cdef StringStore _string_store
    cdef public int i
    cdef public int idx
    cdef public int pos
    cdef int lemma

    cdef public atom_t id
    cdef public atom_t cluster
    cdef public atom_t length
    cdef public atom_t postype
    cdef public atom_t sensetype

    cdef public atom_t sic
    cdef public atom_t norm
    cdef public atom_t shape
    cdef public atom_t asciied
    cdef public atom_t prefix
    cdef public atom_t suffix

    cdef public float prob

    cdef public flags_t flags
