from libc.stdint cimport uint32_t

from numpy cimport ndarray
cimport numpy

from cymem.cymem cimport Pool
from thinc.typedefs cimport atom_t

from .typedefs cimport flags_t, attr_id_t, attr_t
from .parts_of_speech cimport univ_pos_t
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
    

    cdef list _py_tokens
    cdef unicode _string
    cdef tuple _tag_strings
    cdef tuple _dep_strings

    cdef public bint is_tagged
    cdef public bint is_parsed

    cdef int length
    cdef int max_length

    cdef int push_back(self, int i, LexemeOrToken lex_or_tok) except -1

    cpdef long[:,:] to_array(self, object features)


cdef class Token:
    cdef Vocab vocab
    cdef unicode _string

    cdef const TokenC* c
    cdef readonly int i
    cdef int array_len

    
    cdef list _py
    cdef tuple _tag_strings
    cdef tuple _dep_strings

    @staticmethod
    cdef inline Token cinit(Vocab vocab, unicode string,
                            const TokenC* token, int offset, int array_len,
                            list py_tokens, tuple tag_strings, tuple dep_strings):
        assert offset >= 0 and offset < array_len
        if py_tokens[offset] is not None:
            return py_tokens[offset]

        cdef Token self = Token.__new__(Token, vocab, string)

        self.c = token
        self.i = offset
        self.array_len = array_len

        self._py = py_tokens
        self._tag_strings = tag_strings
        self._dep_strings = dep_strings
        py_tokens[offset] = self
        return self
