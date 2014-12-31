from libc.stdint cimport uint8_t

from cymem.cymem cimport Pool

from thinc.learner cimport LinearModel
from thinc.features cimport Extractor
from thinc.typedefs cimport atom_t, feat_t, weight_t, class_t

from preshed.maps cimport PreshMapArray

from .typedefs cimport hash_t, id_t
from .tokens cimport Tokens


cdef int arg_max(const weight_t* scores, const int n_classes) nogil


cdef class Model:
    cdef int n_classes

    cdef int update(self, atom_t* context, class_t guess, class_t gold, int cost) except -1

    cdef object model_loc
    cdef Extractor _extractor
    cdef LinearModel _model

    cdef inline const weight_t* score(self, atom_t* context) except NULL:
        cdef int n_feats
        feats = self._extractor.get_feats(context, &n_feats)
        return self._model.get_scores(feats, n_feats)


cdef class HastyModel:
    cdef Pool mem
    cdef weight_t* _scores
 
    cdef const weight_t* score(self, atom_t* context) except NULL
    cdef int update(self, atom_t* context, class_t guess, class_t gold, int cost) except -1

    cdef int n_classes
    cdef Model _hasty
    cdef Model _full
    cdef readonly int hasty_cnt
    cdef readonly int full_cnt
