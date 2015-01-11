from libc.stdint cimport uint32_t

from cython.view cimport array as cvarray

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
    cdef list tag_names

    cdef TokenC* data

    cdef int length
    cdef int max_length

    cdef int push_back(self, int i, LexemeOrToken lex_or_tok) except -1

    cpdef long[:,:] to_array(self, object features)


cdef class Token:
    cdef cvarray vec

    cdef readonly flags_t flags
   
    cdef readonly attr_t id
    cdef readonly attr_t sic
    cdef readonly attr_t dense
    cdef readonly attr_t shape
    cdef readonly attr_t prefix
    cdef readonly attr_t suffix
 
    cdef readonly attr_t length
    cdef readonly attr_t cluster
    cdef readonly attr_t pos_type

    cdef readonly float prob
    cdef readonly float sentiment

    cdef readonly Morphology morph
    cdef readonly univ_tag_t pos
    cdef readonly int fine_pos
    cdef readonly int idx
    cdef readonly int lemma
    cdef readonly int sense
    cdef readonly int dep_tag
    
    cdef readonly int head_offset
    cdef readonly uint32_t l_kids
    cdef readonly uint32_t r_kids
