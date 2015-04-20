from preshed.maps cimport PreshMapArray
from cymem.cymem cimport Pool

from .._ml cimport Model
from ..strings cimport StringStore
from ..structs cimport TokenC, LexemeC, Morphology, PosTag
from ..parts_of_speech cimport univ_pos_t
from .lemmatizer import Lemmatizer


cdef class EnPosTagger:
    cdef readonly Pool mem
    cdef readonly StringStore strings
    cdef readonly Model model
    cdef public object lemmatizer
    cdef PreshMapArray _morph_cache

    cdef PosTag* tags
    cdef readonly object tag_names
    cdef readonly object tag_map
    cdef readonly int n_tags

    cdef int set_morph(self, const int i, const PosTag* tag, TokenC* tokens) except -1
    cdef int lemmatize(self, const univ_pos_t pos, const LexemeC* lex) except -1
