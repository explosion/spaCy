from libc.stdint cimport uint8_t

from cymem.cymem cimport Pool

from thinc.learner cimport LinearModel
from thinc.features cimport Extractor
from thinc.typedefs cimport atom_t, feat_t, weight_t, class_t

from preshed.maps cimport PreshMapArray

from .typedefs cimport hash_t, id_t
from .tokens cimport Tokens


cdef class Model:
    cdef weight_t* score(self, atom_t* context) except NULL
    cdef class_t predict(self, atom_t* context) except *
    cdef class_t predict_among(self, atom_t* context, bint* valid) except *
    cdef class_t predict_and_update(self, atom_t* context, const bint* valid,
                                    const int* costs) except *
 
    cdef object model_loc
    cdef Extractor _extractor
    cdef LinearModel _model


cdef class HastyModel:
    cdef class_t predict(self, atom_t* context) except *
    cdef class_t predict_among(self, atom_t* context, bint* valid) except *
    cdef class_t predict_and_update(self, atom_t* context, const bint* valid,
                                    const int* costs) except *
 
    cdef weight_t confidence
    cdef int n_classes
    cdef Model _hasty
    cdef Model _full
