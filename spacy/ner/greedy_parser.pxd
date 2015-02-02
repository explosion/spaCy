from cymem.cymem cimport Pool
from thinc.features cimport Extractor
from thinc.learner cimport LinearModel
from thinc.typedefs cimport *

from ..tokens cimport Tokens
from ..typedefs cimport *

from .structs cimport Move
from .annot cimport NERAnnotation


cdef class NERParser:
    cdef Pool mem
    cdef Extractor extractor
    cdef LinearModel model
    cdef readonly list tag_names
    cdef readonly list entity_types
    cdef readonly int n_classes

    cdef Move* _moves
    cdef atom_t* _context
    cdef feat_t* _feats
    cdef weight_t* _values
    cdef weight_t* _scores


    cpdef list train(self, Tokens tokens, NERAnnotation annot)
    cpdef list set_tags(self, Tokens tokens)
