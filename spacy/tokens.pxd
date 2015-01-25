from libc.stdint cimport uint32_t

from numpy cimport ndarray
cimport numpy

from cymem.cymem cimport Pool
from thinc.typedefs cimport atom_t

from .typedefs cimport flags_t, attr_id_t, attr_t, univ_tag_t
from .structs cimport Morphology, TokenC, LexemeC
from .vocab cimport Vocab
from .strings cimport StringStore


ctypedef const LexemeC* const_Lexeme_ptr
ctypedef TokenC* TokenC_ptr

ctypedef fused LexemeOrToken:
    const_Lexeme_ptr
    TokenC_ptr


cdef attr_t get_lex_attr(const LexemeC* lex, attr_id_t feat_name) nogil
cdef attr_t get_token_attr(const TokenC* lex, attr_id_t feat_name) nogil

cdef inline bint check_flag(const LexemeC* lexeme, attr_id_t flag_id) nogil:
    return lexeme.flags & (1 << flag_id)


cdef class Tokens:
    cdef Pool mem
    cdef Vocab vocab
    
    cdef TokenC* data
    

    cdef unicode _string
    cdef list _tag_strings
    cdef list _dep_strings

    cdef public bint is_tagged
    cdef public bint is_parsed

    cdef int length
    cdef int max_length

    cdef int push_back(self, int i, LexemeOrToken lex_or_tok) except -1

    cpdef long[:,:] to_array(self, object features)


cdef class Token:
    cdef readonly Tokens _seq
    cdef readonly int i

    cdef readonly attr_t idx
    cdef readonly attr_t cluster
    cdef readonly attr_t length
    cdef readonly attr_t orth
    cdef readonly attr_t lower
    cdef readonly attr_t norm
    cdef readonly attr_t shape
    cdef readonly attr_t prefix
    cdef readonly attr_t suffix
    cdef readonly float prob
    cdef readonly float sentiment
    cdef readonly attr_t flags
    cdef readonly attr_t lemma
    cdef readonly univ_tag_t pos
    cdef readonly attr_t tag
    cdef readonly attr_t dep
    cdef readonly ndarray repvec
    cdef readonly unicode string
