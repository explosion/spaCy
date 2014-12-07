from cymem.cymem cimport Pool

from thinc.learner cimport LinearModel
from thinc.features cimport Extractor
from thinc.typedefs cimport atom_t, feat_t, weight_t, class_t

from .typedefs cimport hash_t
from .tokens cimport Tokens


cpdef enum TagType:
    POS
    SENSE


cdef class Tagger:
    cpdef int set_tags(self, Tokens tokens) except -1
    cpdef class_t predict(self, int i, Tokens tokens, object golds=*) except 0
 
    cpdef readonly Pool mem
    cpdef readonly Extractor extractor
    cpdef readonly LinearModel model

    cpdef readonly TagType tag_type
    cpdef readonly list tag_names
