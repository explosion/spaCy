from libc.stdint cimport uint32_t

import numpy as np
cimport numpy as np

from cymem.cymem cimport Pool

from .structs cimport Lexeme, TokenC, Morphology

from .typedefs cimport flags_t, attr_t, flags_t

from .strings cimport StringStore


ctypedef const Lexeme* const_Lexeme_ptr
ctypedef TokenC* TokenC_ptr

ctypedef fused LexemeOrToken:
    const_Lexeme_ptr
    TokenC_ptr


cdef class Tokens:
    cdef Pool mem
    cdef StringStore strings
    cdef list tag_names

    cdef TokenC* data

    cdef int length
    cdef int max_length

    cdef int push_back(self, int i, LexemeOrToken lex_or_tok) except -1

    cpdef np.ndarray[long, ndim=2] get_array(self, list features)


cdef class Token:
    cdef public StringStore strings
    cdef public int i
    cdef public int idx
    cdef int pos
    cdef int lemma
    cdef public int head
    cdef public int dep_tag

    cdef public attr_t id
    cdef public attr_t cluster
    cdef public attr_t length
    cdef public attr_t postype
    cdef public attr_t sensetype

    cdef public attr_t sic
    cdef public attr_t norm
    cdef public attr_t shape
    cdef public attr_t asciied
    cdef public attr_t prefix
    cdef public attr_t suffix

    cdef public float prob

    cdef public flags_t flags
