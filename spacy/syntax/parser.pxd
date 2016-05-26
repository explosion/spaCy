from thinc.linear.avgtron cimport AveragedPerceptron
from thinc.neural.nn cimport NeuralNet
from thinc.base cimport Model
from thinc.extra.eg cimport Example

from .stateclass cimport StateClass
from .arc_eager cimport TransitionSystem
from ..tokens.doc cimport Doc
from ..structs cimport TokenC
from thinc.structs cimport ExampleC
from ._state cimport StateC


cdef class ParserNeuralNet(NeuralNet):
    cdef void set_featuresC(self, ExampleC* eg, const StateC* state) nogil

cdef class ParserPerceptron(AveragedPerceptron):
    cdef void set_featuresC(self, ExampleC* eg, const StateC* state) nogil


cdef class Parser:
    cdef readonly ParserNeuralNet model
    cdef readonly TransitionSystem moves
    cdef int _projectivize

    cdef int parseC(self, TokenC* tokens, int length, int nr_feat, int nr_class) with gil
