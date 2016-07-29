from thinc.linear.avgtron cimport AveragedPerceptron
from thinc.neural.nn cimport NeuralNet
from thinc.linear.features cimport ConjunctionExtracter
from thinc.structs cimport NeuralNetC, FeatureC


cdef class ParserNeuralNet(NeuralNet):
    cdef ConjunctionExtracter extracter
    cdef int _set_featuresC(self, FeatureC* feats, const void* _state) nogil


cdef class ParserPerceptron(AveragedPerceptron):
    cdef int _set_featuresC(self, FeatureC* feats, const void* _state) nogil
