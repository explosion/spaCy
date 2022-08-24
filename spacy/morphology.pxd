cimport numpy as np
from libc.stdint cimport uint32_t, uint64_t
from libcpp.unordered_map cimport unordered_map
from libcpp.vector cimport vector
from libcpp.memory cimport shared_ptr

from .strings cimport StringStore
from .typedefs cimport attr_t, hash_t


cdef cppclass Feature:
    hash_t field
    hash_t value

    __init__():
        this.field = 0
        this.value = 0


cdef cppclass MorphAnalysisC:
    hash_t key  
    vector[Feature] features

    __init__():
        this.key = 0

cdef class Morphology:
    cdef readonly StringStore strings
    cdef unordered_map[hash_t, shared_ptr[MorphAnalysisC]] tags

    cdef shared_ptr[MorphAnalysisC] _lookup_tag(self, hash_t tag_hash)
    cdef void _intern_morph_tag(self, hash_t tag_key, feats)
    cdef hash_t _add(self, features)
    cdef str _normalize_features(self, features)
    cdef str get_morph_str(self, hash_t morph_key)
    cdef shared_ptr[MorphAnalysisC] get_morph_c(self, hash_t morph_key)

cdef int check_feature(const shared_ptr[MorphAnalysisC] morph, attr_t feature) nogil
cdef list list_features(const shared_ptr[MorphAnalysisC] morph)
cdef np.ndarray get_by_field(const shared_ptr[MorphAnalysisC] morph, attr_t field)
cdef int get_n_by_field(attr_t* results, const shared_ptr[MorphAnalysisC] morph, attr_t field) nogil
