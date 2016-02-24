from thinc.neural.nn cimport NeuralNet
from thinc.extra.eg cimport Example
from thinc.structs cimport ExampleC

from .structs cimport TokenC
from .vocab cimport Vocab


cdef class TaggerNeuralNet(NeuralNet):
    cdef void set_featuresC(self, ExampleC* eg, const TokenC* tokens, int i) except *
 
cdef class CharacterTagger(NeuralNet):
    cdef readonly int depth
    cdef readonly int hidden_width
    cdef readonly int chars_width
    cdef readonly int tags_width
    cdef readonly float learn_rate
    cdef readonly int left_window
    cdef readonly int right_window
    cdef readonly int tags_window
    cdef readonly int chars_per_word
    cdef void set_featuresC(self, ExampleC* eg, const TokenC* tokens, object strings, int i) except *

cdef class Tagger:
    cdef readonly Vocab vocab
    cdef readonly CharacterTagger model
    cdef public dict freqs
