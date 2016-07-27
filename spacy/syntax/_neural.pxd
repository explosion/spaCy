from thinc.linear.avgtron cimport AveragedPerceptron
from thinc.neural.nn cimport NeuralNet
from thinc.linear.features cimport ConjunctionExtracter
from thinc.structs cimport NeuralNetC, ExampleC


cdef class ParserNeuralNet(NeuralNet):
    cdef ConjunctionExtracter extracter
    cdef void set_featuresC(self, ExampleC* eg, const void* _state) nogil


cdef class ParserPerceptron(AveragedPerceptron):
    cdef void set_featuresC(self, ExampleC* eg, const void* _state) nogil
