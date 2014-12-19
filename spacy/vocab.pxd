from libcpp.vector cimport vector

from preshed.maps cimport PreshMap
from cymem.cymem cimport Pool
from murmurhash.mrmr cimport hash64

from .structs cimport Lexeme, TokenC, UniStr
from .typedefs cimport utf8_t, id_t, hash_t
from .strings cimport StringStore


cdef union LexemesOrTokens:
    const Lexeme* const* lexemes
    TokenC* tokens


cdef struct _Cached:
    LexemesOrTokens data
    bint is_lex
    int length


cdef inline void slice_unicode(UniStr* s, Py_UNICODE* chars, int start, int end) nogil:
    s.chars = &chars[start]
    s.n = end - start
    s.key = hash64(s.chars, s.n * sizeof(Py_UNICODE), 0)


cdef class Vocab:
    cpdef public get_lex_props
    cdef Pool mem
    cpdef readonly StringStore strings
    cdef vector[Lexeme*] lexemes

    cdef const Lexeme* get(self, Pool mem, UniStr* s) except NULL
    
    cdef PreshMap _map
  
