from thinc.linear.avgtron cimport AveragedPerceptron
from thinc.neural.nn cimport NeuralNet
from thinc.linear.features cimport ConjunctionExtracter
from thinc.structs cimport NeuralNetC, FeatureC


cdef class ParserNeuralNet(NeuralNet):
    cdef ConjunctionExtracter extracter


cdef class ParserPerceptron(AveragedPerceptron):
    pass
