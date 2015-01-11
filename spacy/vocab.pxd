from libcpp.vector cimport vector

from preshed.maps cimport PreshMap
from cymem.cymem cimport Pool
from murmurhash.mrmr cimport hash64

from .structs cimport LexemeC, TokenC, UniStr
from .typedefs cimport utf8_t, id_t, hash_t
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
    cpdef public get_lex_props
    cdef Pool mem
    cpdef readonly StringStore strings
    cdef vector[LexemeC*] lexemes

    cdef const LexemeC* get(self, Pool mem, UniStr* s) except NULL
    
    cdef PreshMap _map
  
