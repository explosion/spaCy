from thinc.linear.avgtron cimport AveragedPerceptron
from thinc.extra.eg cimport Example
from thinc.structs cimport ExampleC

from .stateclass cimport StateClass
from .arc_eager cimport TransitionSystem
from ..tokens.doc cimport Doc
from ..structs cimport TokenC


cdef class ParserModel(AveragedPerceptron):
    cdef void set_featuresC(self, ExampleC* eg, StateClass stcls) nogil


cdef class Parser:
    cdef readonly ParserModel model
    cdef readonly TransitionSystem moves

    cdef void parseC(self, Doc tokens, StateClass stcls, Example eg) nogil
