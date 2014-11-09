from cymem.cymem cimport Pool

from thinc.learner cimport LinearModel
from thinc.features cimport Extractor
from thinc.typedefs cimport atom_t, feat_t, weight_t, class_t

from .typedefs cimport hash_t
from .context cimport Slots
from .tokens cimport Tokens


cpdef enum TagType:
    POS
    ENTITY
    SENSE


cdef class Tagger:
    cpdef int set_tags(self, Tokens tokens) except -1
    cpdef class_t predict(self, int i, Tokens tokens) except 0
    cpdef int tell_answer(self, list gold) except -1
 
    cpdef readonly Pool mem
    cpdef readonly Extractor extractor
    cpdef readonly LinearModel model

    cpdef readonly TagType tag_type
    cpdef readonly list tag_names

    cdef class_t _guess
    cdef atom_t* _context
    cdef feat_t* _feats
    cdef weight_t* _values
    cdef weight_t* _scores
