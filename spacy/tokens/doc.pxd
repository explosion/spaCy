from cymem.cymem cimport Pool
cimport numpy as np
from preshed.counter cimport PreshCounter

from ..vocab cimport Vocab
from ..structs cimport TokenC, LexemeC
from ..typedefs cimport attr_t
from ..attrs cimport attr_id_t


cdef attr_t get_token_attr(const TokenC* token, attr_id_t feat_name) nogil


ctypedef const LexemeC* const_Lexeme_ptr
ctypedef TokenC* TokenC_ptr

ctypedef fused LexemeOrToken:
    const_Lexeme_ptr
    TokenC_ptr


cdef class Doc:
    cdef readonly Pool mem
    cdef readonly Vocab vocab

    cdef TokenC* data

    cdef public bint is_tagged
    cdef public bint is_parsed

    cdef public list _py_tokens

    cdef int length
    cdef int max_length

    cdef int push_back(self, LexemeOrToken lex_or_tok, bint trailing_space) except -1

    cpdef np.ndarray to_array(self, object features)

    cdef int set_parse(self, const TokenC* parsed) except -1
