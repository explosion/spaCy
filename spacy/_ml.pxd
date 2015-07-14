from libc.stdint cimport uint8_t

from cymem.cymem cimport Pool

from thinc.learner cimport LinearModel
from thinc.features cimport Extractor, Feature
from thinc.typedefs cimport atom_t, feat_t, weight_t, class_t
from thinc.api cimport ExampleC

from preshed.maps cimport PreshMapArray

from .typedefs cimport hash_t, id_t


cdef int arg_max(const weight_t* scores, const int n_classes) nogil

cdef int arg_max_if_true(const weight_t* scores, const int* is_valid,  int n_classes) nogil

cdef int arg_max_if_zero(const weight_t* scores, const int* costs, int n_classes) nogil


cdef class Model:
    cdef readonly int n_classes
    cdef readonly int n_feats
    
    cdef const weight_t* score(self, atom_t* context) except NULL
    cdef int set_scores(self, weight_t* scores, atom_t* context) nogil

    cdef int update(self, atom_t* context, class_t guess, class_t gold, int cost) except -1
    
    cdef object model_loc
    cdef Extractor _extractor
    cdef LinearModel _model
