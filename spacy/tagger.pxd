from thinc.api cimport AveragedPerceptron
from thinc.api cimport ExampleC

from .structs cimport TokenC
from .vocab cimport Vocab


cdef class TaggerModel(AveragedPerceptron):
    cdef void set_features(self, ExampleC* eg, const TokenC* tokens, int i) except *
    cdef void set_costs(self, ExampleC* eg, int gold) except *
    cdef void update(self, ExampleC* eg) except *
 

cdef class Tagger:
    cdef readonly Vocab vocab
    cdef readonly TaggerModel model
    cdef public dict freqs
