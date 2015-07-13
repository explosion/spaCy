from cymem.cymem cimport Pool
cimport numpy as np
from preshed.counter cimport PreshCounter

from ..vocab cimport Vocab
from ..structs cimport TokenC, LexemeC


ctypedef const LexemeC* const_Lexeme_ptr
ctypedef TokenC* TokenC_ptr

ctypedef fused LexemeOrToken:
    const_Lexeme_ptr
    TokenC_ptr


cdef class Doc:
    cdef Pool mem
    cdef Vocab vocab

    cdef TokenC* data

    cdef public bint is_tagged
    cdef public bint is_parsed

    cdef int length
    cdef int max_length

    cdef int push_back(self, int i, LexemeOrToken lex_or_tok) except -1

    cpdef np.ndarray to_array(self, object features)

    cdef int set_parse(self, const TokenC* parsed) except -1
