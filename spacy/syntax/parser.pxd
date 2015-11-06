from thinc.search cimport Beam
from thinc.api cimport AveragedPerceptron
from thinc.api cimport Example, ExampleC

from .stateclass cimport StateClass
from .arc_eager cimport TransitionSystem
from ..tokens.doc cimport Doc
from ..structs cimport TokenC


cdef class ParserModel(AveragedPerceptron):
    cdef void set_features(self, ExampleC* eg, StateClass stcls) except *


cdef class Parser:
    cdef readonly ParserModel model
    cdef readonly TransitionSystem moves
