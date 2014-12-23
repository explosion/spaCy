from preshed.maps cimport PreshMapArray

from ..tagger cimport Tagger
from ..strings cimport StringStore
from ..structs cimport TokenC, Lexeme, Morphology, PosTag
from ..typedefs cimport univ_tag_t
from .lemmatizer import Lemmatizer


cdef class EnPosTagger(Tagger):
    cdef readonly StringStore strings
    cdef public object lemmatizer
    cdef PreshMapArray _morph_cache

    cdef PosTag* tags
    cdef readonly object tag_names
    cdef readonly object tag_map

    cdef int set_morph(self, const int i, TokenC* tokens) except -1
    cdef int lemmatize(self, const univ_tag_t pos, const Lexeme* lex) except -1

