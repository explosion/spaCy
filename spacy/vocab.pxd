from libcpp.vector cimport vector

from preshed.maps cimport PreshMap
from cymem.cymem cimport Pool
from murmurhash.mrmr cimport hash64

from .structs cimport LexemeC, TokenC, UniStr
from .typedefs cimport utf8_t, hash_t
from .strings cimport StringStore


cdef LexemeC EMPTY_LEXEME


cdef union LexemesOrTokens:
    const LexemeC* const* lexemes
    TokenC* tokens


cdef struct _Cached:
    LexemesOrTokens data
    bint is_lex
    int length


cdef class Vocab:
    cpdef public lexeme_props_getter
    cdef Pool mem
    cpdef readonly StringStore strings
    cdef readonly object pos_tags
    cdef readonly int length

    cdef const LexemeC* get(self, Pool mem, UniStr* s) except NULL
    cdef int _add_lex_to_vocab(self, hash_t key, const LexemeC* lex) except -1

    cdef PreshMap _by_hash
    cdef PreshMap _by_orth
    cdef readonly int repvec_length
