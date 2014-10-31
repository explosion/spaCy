from cymem.cymem cimport Pool

from thinc.learner cimport LinearModel
from thinc.features cimport Extractor
from thinc.typedefs cimport atom_t, feat_t, weight_t, class_t

from .tokens cimport Tokens


cdef class Tagger:
    cpdef readonly Extractor extractor
    cpdef readonly LinearModel model

    cpdef class_t predict(self, int i, Tokens tokens, class_t prev, class_t prev_prev) except 0
    cpdef bint tell_answer(self, class_t gold_tag) except *
 
    cdef Pool mem
    cdef class_t _guess
    cdef atom_t* _atoms
    cdef feat_t* _feats
    cdef weight_t* _values
    cdef weight_t* _scores
