from thinc.linear.avgtron cimport AveragedPerceptron
from thinc.extra.eg cimport Example
from thinc.structs cimport ExampleC, FeatureC

from .structs cimport TokenC
from .vocab cimport Vocab


cdef class TaggerModel(AveragedPerceptron):
    cdef int set_featuresC(self, FeatureC* feats, const void* _token) nogil
 

cdef class Tagger:
    cdef readonly Vocab vocab
    cdef readonly TaggerModel model
    cdef public dict freqs
