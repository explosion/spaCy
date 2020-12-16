from cymem.cymem cimport Pool
from preshed.maps cimport PreshMap, PreshMapArray
from libc.stdint cimport uint64_t
from murmurhash cimport mrmr

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
    cdef readonly object exc
    cdef readonly object _feat_map
    cdef readonly PreshMapArray _cache
    cdef readonly int n_tags

    cpdef update(self, hash_t morph, features)
    cdef hash_t insert(self, MorphAnalysisC tag) except 0
    
    cdef int assign_untagged(self, TokenC* token) except -1
    cdef int assign_tag(self, TokenC* token, tag) except -1
    cdef int assign_tag_id(self, TokenC* token, int tag_id) except -1

    cdef int _assign_tag_from_exceptions(self, TokenC* token, int tag_id) except -1


cdef int check_feature(const MorphAnalysisC* tag, attr_t feature) nogil
cdef attr_t get_field(const MorphAnalysisC* tag, int field) nogil
cdef list list_features(const MorphAnalysisC* tag)

cdef tag_to_json(const MorphAnalysisC* tag)
