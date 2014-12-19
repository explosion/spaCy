from cymem.cymem cimport Pool
from preshed.maps cimport PreshMapArray

from .structs cimport TokenC, Lexeme, Morphology, PosTag
from .strings cimport StringStore
from .typedefs cimport id_t, univ_tag_t


cdef class Morphologizer:
    cdef Pool mem
    cdef StringStore strings
    cdef object lemmatizer
    cdef PosTag* tags
    cdef readonly list tag_names

    cdef PreshMapArray _cache
    cdef int lemmatize(self, const univ_tag_t pos, const Lexeme* lex) except -1
    cdef int set_morph(self, const int i, TokenC* tokens) except -1
