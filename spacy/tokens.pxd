from libc.stdint cimport uint32_t

from cython.view cimport array as cvarray

from cymem.cymem cimport Pool
from thinc.typedefs cimport atom_t

from .typedefs cimport flags_t, attr_id_t, attr_t
from .structs cimport Morphology, TokenC, Lexeme
from .vocab cimport Vocab
from .strings cimport StringStore


ctypedef const Lexeme* const_Lexeme_ptr
ctypedef TokenC* TokenC_ptr

ctypedef fused LexemeOrToken:
    const_Lexeme_ptr
    TokenC_ptr


cdef attr_t get_lex_attr(const Lexeme* lex, attr_id_t feat_name) nogil
cdef attr_t get_token_attr(const TokenC* lex, attr_id_t feat_name) nogil

cdef inline bint check_flag(const Lexeme* lexeme, attr_id_t flag_id) nogil:
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
    cdef Tokens _seq
    cdef readonly int i
