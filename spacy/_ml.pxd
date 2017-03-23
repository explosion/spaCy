from thinc.linear.features cimport ConjunctionExtracter
from thinc.typedefs cimport atom_t, weight_t
from thinc.structs cimport FeatureC
from libc.stdint cimport uint32_t, uint64_t
cimport numpy as np
from cymem.cymem cimport Pool
from libcpp.vector cimport vector


cdef class LinearModel:
    cdef ConjunctionExtracter extracter
    cdef readonly int nr_class
    cdef readonly uint32_t nr_weight
    cdef public weight_t learn_rate
    cdef Pool mem
    cdef weight_t* W
    cdef weight_t* d_W
    cdef vector[uint64_t]* _indices

    cdef void hinge_lossC(self, weight_t* d_scores,
            const weight_t* scores, const weight_t* costs) nogil

    cdef void log_lossC(self, weight_t* d_scores,
            const weight_t* scores, const weight_t* costs) nogil

    cdef void regression_lossC(self, weight_t* d_scores,
            const weight_t* scores, const weight_t* costs) nogil

    cdef void set_scoresC(self, weight_t* scores,
            const FeatureC* features, int nr_feat) nogil

    cdef void set_gradientC(self, const weight_t* d_scores, const FeatureC*
            features, int nr_feat) nogil
