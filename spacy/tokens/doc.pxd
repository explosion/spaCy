cimport numpy as np
from cymem.cymem cimport Pool

from ..attrs cimport attr_id_t
from ..structs cimport LexemeC, SpanC, TokenC
from ..typedefs cimport attr_t
from ..vocab cimport Vocab


cdef attr_t get_token_attr(const TokenC* token, attr_id_t feat_name) nogil
cdef attr_t get_token_attr_for_matcher(const TokenC* token, attr_id_t feat_name) nogil


ctypedef const LexemeC* const_Lexeme_ptr
ctypedef const TokenC* const_TokenC_ptr

ctypedef fused LexemeOrToken:
    const_Lexeme_ptr
    const_TokenC_ptr


cdef int set_children_from_heads(TokenC* tokens, int start, int end) except -1


cdef int _set_lr_kids_and_edges(TokenC* tokens, int start, int end, int loop_count) except -1


cdef int token_by_start(const TokenC* tokens, int length, int start_char) except -2


cdef int token_by_end(const TokenC* tokens, int length, int end_char) except -2


cdef int [:, :] _get_lca_matrix(Doc, int start, int end)


cdef class Doc:
    cdef readonly Pool mem
    cdef readonly Vocab vocab

    cdef public object _vector
    cdef public object _vector_norm

    cdef public object tensor
    cdef public object cats
    cdef public object user_data
    cdef readonly object spans

    cdef TokenC* c

    cdef public float sentiment

    cdef public dict user_hooks
    cdef public dict user_token_hooks
    cdef public dict user_span_hooks

    cdef public bint has_unknown_spaces

    cdef public object _context

    cdef int length
    cdef int max_length

    cdef public object noun_chunks_iterator

    cdef object __weakref__

    cdef int push_back(self, LexemeOrToken lex_or_tok, bint has_space) except -1

    cpdef np.ndarray to_array(self, object features)
