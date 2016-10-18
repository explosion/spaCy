from thinc.linear.avgtron cimport AveragedPerceptron
from thinc.extra.eg cimport Example
from thinc.structs cimport ExampleC

from .structs cimport TokenC
from .vocab cimport Vocab


cdef class TaggerModel(AveragedPerceptron):
    cdef void set_featuresC(self, ExampleC* eg, const TokenC* tokens, int i) except *
 

cdef class Tagger:
    cdef readonly Vocab vocab
    cdef readonly TaggerModel model
    cdef public dict freqs
    cdef public object cfg
