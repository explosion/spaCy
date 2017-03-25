from thinc.linear.avgtron cimport AveragedPerceptron
from thinc.typedefs cimport atom_t
from thinc.structs cimport FeatureC

from .stateclass cimport StateClass
from .arc_eager cimport TransitionSystem
from ..vocab cimport Vocab
from ..tokens.doc cimport Doc
from ..structs cimport TokenC
from ._state cimport StateC


cdef class ParserModel(AveragedPerceptron):
    cdef int set_featuresC(self, atom_t* context, FeatureC* features,
                            const StateC* state) nogil


cdef class Parser:
    cdef readonly Vocab vocab
    cdef readonly ParserModel model
    cdef readonly TransitionSystem moves
    cdef readonly object cfg

    cdef int parseC(self, TokenC* tokens, int length, int nr_feat) nogil
