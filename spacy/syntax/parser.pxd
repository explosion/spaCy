from thinc.linear.avgtron cimport AveragedPerceptron
from thinc.extra.eg cimport Example
from thinc.structs cimport ExampleC

from .stateclass cimport StateClass
from .arc_eager cimport TransitionSystem
from ..tokens.doc cimport Doc
from ..structs cimport TokenC
from ._state cimport StateC


cdef class ParserModel(AveragedPerceptron):
    cdef void set_featuresC(self, ExampleC* eg, const StateC* state) nogil

cdef class Parser:
    cdef readonly ParserModel model
    cdef readonly TransitionSystem moves
    cdef int _projectivize

    cdef int parseC(self, TokenC* tokens, int length, int nr_feat, int nr_class) nogil
