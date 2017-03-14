from thinc.linear.avgtron cimport AveragedPerceptron
from thinc.linear.features cimport ConjunctionExtracter
from thinc.typedefs cimport atom_t, weight_t
from thinc.structs cimport FeatureC

from .stateclass cimport StateClass
from .arc_eager cimport TransitionSystem
from ..vocab cimport Vocab
from ..tokens.doc cimport Doc
from ..structs cimport TokenC
from ._state cimport StateC
from .._ml cimport LinearModel


cdef class ParserModel(LinearModel):
    cdef int set_featuresC(self, atom_t* context, FeatureC* features,
                            const StateC* state) nogil
 
 
cdef class Parser:
    cdef readonly Vocab vocab
    cdef readonly ParserModel model
    cdef readonly TransitionSystem moves
    cdef readonly object cfg
    cdef public object optimizer

    cdef int parseC(self, TokenC* tokens, int length, int nr_feat, int nr_class) with gil
