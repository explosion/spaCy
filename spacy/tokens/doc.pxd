from cymem.cymem cimport Pool
cimport numpy as np
from preshed.counter cimport PreshCounter

from ..vocab cimport Vocab
from ..structs cimport TokenC, LexemeC
from ..typedefs cimport attr_t
from ..attrs cimport attr_id_t


cdef attr_t get_token_attr(const TokenC* token, attr_id_t feat_name) nogil


ctypedef const LexemeC* const_Lexeme_ptr
ctypedef const TokenC* const_TokenC_ptr

ctypedef fused LexemeOrToken:
    const_Lexeme_ptr
    const_TokenC_ptr


cdef int token_by_start(const TokenC* tokens, int length, int start_char) except -2


cdef int token_by_end(const TokenC* tokens, int length, int end_char) except -2


cdef class Doc:
    cdef readonly Pool mem
    cdef readonly Vocab vocab

    cdef public object _vector
    cdef public object _vector_norm

    cdef public np.ndarray tensor
    cdef public object user_data

    cdef TokenC* c

    cdef public bint is_tagged
    cdef public bint is_parsed

    cdef public float sentiment

    cdef public dict user_hooks
    cdef public dict user_token_hooks
    cdef public dict user_span_hooks

    cdef public list _py_tokens

    cdef int length
    cdef int max_length

    cdef public object noun_chunks_iterator

    cdef int push_back(self, LexemeOrToken lex_or_tok, bint trailing_space) except -1

    cpdef np.ndarray to_array(self, object features)

    cdef void set_parse(self, const TokenC* parsed) nogil
