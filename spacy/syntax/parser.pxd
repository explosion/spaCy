from thinc.linear.avgtron cimport AveragedPerceptron
from thinc.neural.nn cimport NeuralNet
from thinc.linear.features cimport ConjunctionExtracter
from thinc.base cimport Model
from thinc.extra.eg cimport Example
from thinc.typedefs cimport weight_t
from thinc.structs cimport FeatureC

from .stateclass cimport StateClass
from .arc_eager cimport TransitionSystem
from ..tokens.doc cimport Doc
from ..structs cimport TokenC
from thinc.structs cimport NeuralNetC, ExampleC
from ._state cimport StateC


cdef class ParserNeuralNet(NeuralNet):
    cdef ConjunctionExtracter extracter
    cdef void set_featuresC(self, ExampleC* eg, const void* _state) nogil


cdef class ParserPerceptron(AveragedPerceptron):
    cdef void set_featuresC(self, ExampleC* eg, const void* _state) nogil


cdef class ParserNeuralNetEnsemble(ParserNeuralNet):
    cdef object _models
    cdef NeuralNetC** _models_c
    cdef int** _masks
    cdef int _nr_model

    
cdef class Parser:
    cdef readonly Model model
    cdef readonly TransitionSystem moves
    cdef int _projectivize

    cdef int parseC(self, TokenC* tokens, int length, int nr_feat, int nr_class) with gil
