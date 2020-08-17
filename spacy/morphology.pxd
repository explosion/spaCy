from cymem.cymem cimport Pool
from preshed.maps cimport PreshMap, PreshMapArray
from libc.stdint cimport uint64_t
from murmurhash cimport mrmr
cimport numpy as np

from .structs cimport TokenC, MorphAnalysisC
from .strings cimport StringStore
from .typedefs cimport hash_t, attr_t, flags_t
from .parts_of_speech cimport univ_pos_t
from . cimport symbols


cdef class Morphology:
    cdef readonly Pool mem
    cdef readonly StringStore strings
    cdef PreshMap tags # Keyed by hash, value is pointer to tag

    cdef public object lemmatizer
    cdef readonly object tag_map
    cdef readonly object tag_names
    cdef readonly object reverse_index
    cdef readonly object _exc
    cdef readonly PreshMapArray _cache
    cdef readonly int n_tags

    cdef MorphAnalysisC create_morph_tag(self, field_feature_pairs) except *
    cdef int insert(self, MorphAnalysisC tag) except -1


cdef int check_feature(const MorphAnalysisC* morph, attr_t feature) nogil
cdef list list_features(const MorphAnalysisC* morph)
cdef np.ndarray get_by_field(const MorphAnalysisC* morph, attr_t field)
cdef int get_n_by_field(attr_t* results, const MorphAnalysisC* morph, attr_t field) nogil
