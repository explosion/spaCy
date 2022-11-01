from cymem.cymem cimport Pool
cimport numpy as np

from ..vocab cimport Vocab
from ..structs cimport TokenC, LexemeC, SpanC
from ..typedefs cimport attr_t
from ..attrs cimport attr_id_t


cdef attr_t get_token_attr(const TokenC* token, attr_id_t feat_name) nogil
cdef attr_t get_token_attr_for_matcher(const TokenC* token, attr_id_t feat_name) nogil    

ctypedef const LexemeC* const_Lexeme_ptr
ctypedef const TokenC* const_TokenC_ptr

ctypedef fused LexemeOrToken:
    const_Lexeme_ptr
    const_TokenC_ptr


cdef extern from "unicodeobject.h":
    bint Py_UNICODE_ISUPPER(Py_UCS4 ch)
    Py_UCS4 Py_UNICODE_TOLOWER(Py_UCS4 ch)


cdef int set_children_from_heads(TokenC* tokens, int start, int end) except -1


cdef int _set_lr_kids_and_edges(TokenC* tokens, int start, int end, int loop_count) except -1


cdef int token_by_start(const TokenC* tokens, int length, int start_char) except -2


cdef int token_by_end(const TokenC* tokens, int length, int end_char) except -2


cdef int [:,:] _get_lca_matrix(Doc, int start, int end)


cdef void _set_prefix_lengths(
    const unsigned char* tok_str,
    const int tok_str_l,
    unsigned char* pref_l_buf,
    const int p_max_l, 
) nogil


cdef void _set_suffix_lengths(
    const unsigned char* tok_str,
    const int tok_str_l,
    unsigned char* suff_l_buf,
    const int s_max_l, 
)


cdef void _search_for_chars(
    const unsigned char* tok_str,
    const int tok_str_l,
    const unsigned char* s_1byte_ch,
    const int s_1byte_ch_l,
    const unsigned char* s_2byte_ch,
    const int s_2byte_ch_l,
    const unsigned char* s_3byte_ch,
    const int s_3byte_ch_l,
    const unsigned char* s_4byte_ch,
    const int s_4byte_ch_l,
    unsigned char* res_buf,
    int max_res_l,
    unsigned char* l_buf,
    bint suffs_not_prefs
) nogil



cdef int _write_hashes(
    const unsigned char* res_buf,
    const unsigned char* aff_l_buf,
    const unsigned char* offset_buf,
    const int end_idx,
    np.ndarray[np.int64_t, ndim=2] hashes,
    const int tok_i,
    const int start_hash_idx,
)  


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
