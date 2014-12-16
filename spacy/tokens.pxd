from libc.stdint cimport uint32_t

import numpy as np
cimport numpy as np

from cymem.cymem cimport Pool
from thinc.typedefs cimport atom_t

from .lexeme cimport Lexeme

from .typedefs cimport flags_t
from .typedefs cimport Morphology
from .lang cimport Language



cdef struct TokenC:
    const Lexeme* lex
    Morphology morph
    int idx
    int pos
    int lemma
    int sense
    int head
    int dep_tag
    uint32_t l_kids
    uint32_t r_kids


ctypedef const Lexeme* const_Lexeme_ptr
ctypedef TokenC* TokenC_ptr

ctypedef fused LexemeOrToken:
    const_Lexeme_ptr
    TokenC_ptr


cdef class Tokens:
    cdef Pool mem
    cdef Language lang
    cdef list tag_names

    cdef TokenC* data

    cdef int length
    cdef int max_length

    cdef int push_back(self, int i, LexemeOrToken lex_or_tok) except -1

    cpdef np.ndarray[long, ndim=2] get_array(self, list features)


cdef class Token:
    cdef public Language lang
    cdef public int i
    cdef public int idx
    cdef int pos
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
