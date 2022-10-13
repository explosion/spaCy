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


cdef int set_children_from_heads(TokenC* tokens, int start, int end) except -1


cdef int _set_lr_kids_and_edges(TokenC* tokens, int start, int end, int loop_count) except -1


cdef int token_by_start(const TokenC* tokens, int length, int start_char) except -2


cdef int token_by_end(const TokenC* tokens, int length, int end_char) except -2


cdef int [:,:] _get_lca_matrix(Doc, int start, int end)


cdef void _populate_affix_buf(
    const void* str_data_ptr,
    const unsigned int unicode_byte_width,
    const int word_idx, 
    const int word_len,
    Py_UCS4* affix_buf, 
    const int pref_length, 
    const int suff_length,
    const bint to_lower
)

cdef const unsigned char[:] _get_utf16_memoryview(str unicode_string, const bint check_2_bytes)


cdef bint _is_searched_char_in_search_chars_v(
    const unsigned short searched_char, 
    const unsigned char[:] search_chars_v,
    const unsigned int search_chars_v_len,
)


cdef void _set_found_char_buf(
    const bint suffs_not_prefs,
    const unsigned char[:] searched_string_v,
    const unsigned int searched_string_len,
    const unsigned char[:] search_chars_v,
    const unsigned int search_chars_v_len,
    char* found_char_buf, 
    const unsigned int found_char_buf_len, 
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
