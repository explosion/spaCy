from cymem.cymem cimport Pool
from thinc.features cimport Extractor
from thinc.learner cimport LinearModel
from thinc.typedefs cimport *

from ..tokens cimport Tokens
from ..typedefs cimport *

from .moves cimport Move


cdef class NERParser:
    cdef Pool mem
    cdef Extractor extractor
    cdef LinearModel model

    cdef Move* _moves
    cdef atom_t* _context
    cdef feat_t* _feats
    cdef weight_t* _values
    cdef weight_t* _scores


    cpdef int train(self, Tokens tokens, golds)
    cpdef int set_tags(self, Tokens tokens) except -1
